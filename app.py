import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

st.set_page_config(page_title="揚水試験リアルタイムダッシュボード", layout="wide")


def get_status_and_color(util: float):
    if util >= 80:
        return "稼働中", "#16a34a"
    if util >= 50:
        return "注意", "#f59e0b"
    return "停止", "#ef4444"


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
    util = metric.get("util", 0)
    status, color = get_status_and_color(util)

    card_html = f"""
    <div style="border:1px solid #e6e6e6;border-radius:8px;padding:16px;box-shadow:0 2px 6px rgba(0,0,0,0.04);background:#fff;">
      <div style="font-size:16px;font-weight:700;color:#111;">{name}</div>
      <div style="margin-top:8px;display:flex;align-items:center;justify-content:space-between;">
        <div style="font-size:24px;font-weight:700;color:#0f172a;">{value}</div>
        <div style="text-align:right;">
          <div style="font-size:12px;color:#666;">稼働率</div>
          <div style="margin-top:6px;padding:6px 12px;border-radius:14px;background:{color};color:#fff;font-weight:700;">{status}</div>
        </div>
      </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def main():
    st.title("揚水試験リアルタイム稼働ダッシュボード")
    st.write(f"更新時刻: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    st.caption("サンプルデータを表示します。稼働率で状態を判定しています。")

    cols = st.columns(5)
    for col, metric in zip(cols, SAMPLE_METRICS):
        with col:
            render_card(metric)

    st.markdown("---")

    # サンプルの水位時系列データ（経過時間：分）
    minutes = list(range(0, 30))
    np.random.seed(42)
    base_level = 3.0
    trend = np.linspace(0, 0.15, len(minutes))
    noise = np.random.normal(0, 0.05, size=len(minutes))
    water_levels = (base_level + trend + noise).round(2)
    
    # 揚水量のサンプルデータ
    base_pump = 100
    pump_trend = np.linspace(0, 30, len(minutes))
    pump_noise = np.random.normal(0, 5, size=len(minutes))
    pump_amounts = (base_pump + pump_trend + pump_noise).round(1)

    df = pd.DataFrame({
        "elapsed_min": minutes, 
        "water_level_m": water_levels,
        "pump_amount_m3_h": pump_amounts
    }).set_index("elapsed_min")

    st.subheader("水位（時系列）")
    st.caption("左軸：水位（m）、右軸：揚水量（m³/h）、横軸：経過時間（分）")
    
    # 水位のラインチャート
    df_reset = df.reset_index()
    line = alt.Chart(df_reset).mark_line(color='steelblue', size=2).encode(
        x=alt.X('elapsed_min:Q', axis=alt.Axis(labelFontSize=16, titleFontSize=16, title='経過時間（分）')),
        y=alt.Y('water_level_m:Q', scale=alt.Scale(domain=[5, None]), axis=alt.Axis(labelFontSize=16, titleFontSize=16, title='水位（m）'))
    )
    
    # 低水位4.0mの赤い線（左軸）
    limit_line = alt.Chart(pd.DataFrame({'limit': [4.0]})).mark_rule(color='red', strokeDash=[5, 5]).encode(
        y=alt.Y('limit:Q', scale=alt.Scale(domain=[5, None]), axis=None)
    )
    
    # 揚水量のラインチャート（右軸）
    pump_line = alt.Chart(df_reset).mark_line(color='orange', size=2).encode(
        x='elapsed_min:Q',
        y=alt.Y('pump_amount_m3_h:Q', axis=alt.Axis(labelFontSize=16, titleFontSize=16, title='揚水量（m³/h）', orient='right'))
    )
    
    # グラフを重ねる
    chart = (line + limit_line + pump_line).properties(width=600, height=400).resolve_scale(y='independent')
    st.altair_chart(chart, use_container_width=True)    

    st.markdown("**凡例**：稼働中（80%以上：緑） / 注意（50-79%：黄） / 停止（50%未満：赤）")


if __name__ == "__main__":
    main()
