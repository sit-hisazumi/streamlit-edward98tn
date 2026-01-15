import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

st.set_page_config(page_title="揚水試験リアルタイムダッシュボード", layout="wide")


def get_status_and_color(name: str, numeric_value: float):
    """メトリクス名に基づいて状態と色を決定"""
    if name == "水位":
        if numeric_value > 4:
            return "注意", "#f59e0b"
        return "正常", "#16a34a"
    elif name == "揚水量":
        if numeric_value == 0:
            return "停止", "#ef4444"
        return "運転中", "#16a34a"
    elif name == "バルブ開閉率":
        if numeric_value == 0:
            return "閉", "#ef4444"
        return "開", "#16a34a"
    elif name == "揚水圧力":
        if numeric_value > 1:
            return "注意", "#f59e0b"
        return "正常", "#16a34a"
    elif name == "ポンプ電流値":
        if numeric_value > 10:
            return "注意", "#f59e0b"
        return "正常", "#16a34a"
    # デフォルト
    return "不明", "#666666"


SAMPLE_METRICS = [
    {"name": "水位", "value": "3.20 m", "util": 70},
    {"name": "揚水量", "value": "120 m<sup>3</sup>/h", "util": 90},
    {"name": "バルブ開閉率", "value": "60%", "util": 60},
    {"name": "揚水圧力", "value": "1.8 MPa", "util": 55},
    {"name": "ポンプ電流値", "value": "45 A", "util": 48},
]


def render_card(metric: dict):
    name = metric.get("name")
    value = metric.get("value")
    numeric_value = metric.get("numeric_value", 0)
    status, color = get_status_and_color(name, numeric_value)

    card_html = f"""
    <div style="border:1px solid #e6e6e6;border-radius:8px;padding:16px;box-shadow:0 2px 6px rgba(0,0,0,0.04);background:#fff;">
      <div style="font-size:16px;font-weight:700;color:#111;">{name}</div>
      <div style="margin-top:8px;display:flex;align-items:center;justify-content:space-between;">
        <div style="font-size:24px;font-weight:700;color:#0f172a;">{value}</div>
        <div style="text-align:right;">
          <div style="margin-top:6px;padding:6px 12px;border-radius:14px;background:{color};color:#fff;font-weight:700;">{status}</div>
        </div>
      </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def main():
    st.title("揚水試験リアルタイム稼働ダッシュボード")
    st.write(f"更新時刻: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    st.caption("Sample.xlsxから実データを表示します。稼働率で状態を判定しています。")
    
    # Sample.xlsxから実データを読み込む
    try:
        excel_file = pd.ExcelFile('Sample.xlsx')
        df_excel = pd.read_excel('Sample.xlsx', sheet_name=0)
        
        # Excelファイルのカラムから最新の値を取得
        latest_row = df_excel.iloc[-1]
        
        # メトリクスを更新
        water_level = latest_row.get('水位', 0)
        pump_amount = latest_row.get('揚水量', 0)
        valve_opening = latest_row.get('バルブ開閉率', 0)
        pressure = latest_row.get('揚水圧力', 0)
        pump_current = latest_row.get('ポンプ電流値', 0)
        
        METRICS = [
            {"name": "水位", "value": f"{water_level:.2f} m", "numeric_value": water_level},
            {"name": "揚水量", "value": f"{pump_amount:.1f} L/min", "numeric_value": pump_amount},
            {"name": "バルブ開閉率", "value": f"{valve_opening:.0f}%", "numeric_value": valve_opening},
            {"name": "揚水圧力", "value": f"{pressure:.1f} MPa", "numeric_value": pressure},
            {"name": "ポンプ電流値", "value": f"{pump_current:.0f} A", "numeric_value": pump_current},
        ]
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        METRICS = SAMPLE_METRICS

    cols = st.columns(5)
    for col, metric in zip(cols, METRICS):
        with col:
            render_card(metric)

    st.markdown("---")

    # Sample.xlsxから時系列データを読み込む
    try:
        df_excel = pd.read_excel('Sample.xlsx', sheet_name=0)
        
        # 必要なカラムが存在するか確認
        if '水位' in df_excel.columns and '揚水量' in df_excel.columns:
            df_reset = df_excel[['水位', '揚水量']].copy()
            df_reset['経緯時間（min）'] = range(len(df_reset))
            df_reset.rename(columns={'水位': '水位（m）', '揚水量': '揚水量（L/min）'}, inplace=True)
        else:
            st.error("Sample.xlsxに水位と揚水量のカラムが見つかりません")
            df_reset = None
    except Exception as e:
        st.error(f"データ読み込みエラー: {e}")
        df_reset = None

    if df_reset is not None and len(df_reset) > 0:
        st.subheader("水位（時系列）")
        st.caption("左軸：水位（m）、右軸：揚水量（L/min）、横軸：経緯時間（min）")
        
        # 水位の最小値と最大値から自動調整
        water_level_min = df_reset['水位（m）'].min()
        water_level_max = df_reset['水位（m）'].max()
        # 余裕を持たせる（最小値から10%下、最大値に10%上）
        margin = (water_level_max - water_level_min) * 0.1 if water_level_max > water_level_min else 0.5
        y_min = water_level_min - margin
        y_max = water_level_max + margin
        
        # スクロールズーム機能
        brush = alt.selection_interval(encodings=['x'])
        
        line = alt.Chart(df_reset).mark_line(color='steelblue', size=2).encode(
            x=alt.X('経緯時間（min）:Q', axis=alt.Axis(labelFontSize=16, titleFontSize=16, title='経緯時間（min）')),
            y=alt.Y('水位（m）:Q', scale=alt.Scale(domain=[y_min, y_max]), axis=alt.Axis(labelFontSize=16, titleFontSize=16, title='水位（m）'))
        ).add_selection(brush)
        
        # 低水位4.0mの赤い線（左軸）
        limit_line = alt.Chart(pd.DataFrame({'limit': [4.0]})).mark_rule(color='red', strokeDash=[5, 5]).encode(
            y=alt.Y('limit:Q', scale=alt.Scale(domain=[y_min, y_max]), axis=None)
        )
        
        # 揚水量のラインチャート（右軸）
        pump_line = alt.Chart(df_reset).mark_line(color='orange', size=2).encode(
            x='経緯時間（min）:Q',
            y=alt.Y('揚水量（L/min）:Q', axis=alt.Axis(labelFontSize=16, titleFontSize=16, title='揚水量（L/min）', orient='right'))
        )
        
        # グラフを重ねる
        chart = (line + limit_line + pump_line).properties(width=600, height=400).resolve_scale(y='independent').encode(x='経緯時間（min）:Q')
        st.altair_chart(chart, use_container_width=True)

    st.markdown("**凡例**：稼働中（80%以上：緑） / 注意（50-79%：黄） / 停止（50%未満：赤）")


if __name__ == "__main__":
    main()
