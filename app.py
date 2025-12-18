import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="揚水試験リアルタイムダッシュボード", layout="wide")


def get_status_and_color(util: float):
    if util >= 80:
        return "稼働中", "#16a34a"
    if util >= 50:
        return "注意", "#f59e0b"
    return "停止", "#ef4444"


SAMPLE_METRICS = [
    {"name": "揚水量", "value": "120 m3/h", "util": 90},
    {"name": "水位", "value": "3.2 m", "util": 70},
    {"name": "揚水圧力", "value": "1.8 MPa", "util": 55},
    {"name": "ポンプ電流値", "value": "45 A", "util": 48},
    {"name": "バブル開閉率", "value": "60%", "util": 60},
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
    water_levels = (base_level + trend + noise).round(3)

    df = pd.DataFrame({"elapsed_min": minutes, "water_level_m": water_levels}).set_index("elapsed_min")

    st.subheader("水位（時系列）")
    st.caption("縦軸：水位（m）、横軸：経過時間（分）")
    st.line_chart(df["water_level_m"])    

    st.markdown("**凡例**：稼働中（80%以上：緑） / 注意（50-79%：黄） / 停止（50%未満：赤）")


if __name__ == "__main__":
    main()
