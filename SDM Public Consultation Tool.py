import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# ---------- Data (from your table) ----------
def mmss_to_seconds(mmss: str) -> int:
    m, s = mmss.split(":")
    return int(m) * 60 + int(s)

data = [
    # stations, yearly_savings (£), overall_impact_s, overall_avg, night_impact_s, night_avg, invest_millions_20yr
    (1,  678_642.90, 1,  "04:48", 0,  "04:47",  8.079082143),
    (2, 1_357_285.80, 1,  "04:48", 1,  "04:48", 16.15816429),
    (3, 2_035_928.70, 2,  "04:49", 3,  "04:50", 24.23724643),
    (4, 2_714_571.60, 2,  "04:49", 5,  "04:52", 32.31632857),
    (5, 3_393_214.50, 3,  "04:50", 6,  "04:53", 40.39541071),
    (6, 4_071_857.40, 4,  "04:51", 7,  "04:54", 48.47449286),
    (7, 4_750_500.30, 5,  "04:52", 9,  "04:56", 56.55357514),
    (8, 5_429_143.20, 6,  "04:53", 13, "05:00", 64.63265714),
    (9, 6_107_786.10, 7,  "04:54", 13, "05:03", 72.71173929),
    (10,6_786_429.00, 8,  "04:55", 18, "05:05", 80.79082143),
    (11,7_465_071.90, 9,  "04:56", 20, "05:07", 88.86990357),
]
df = pd.DataFrame(data, columns=[
    "StationsMoved","YearlySavings","OverallImpact_s","OverallAvg_mmss",
    "NightImpact_s","NightAvg_mmss","Invest_20yr_million"
])

# Derive seconds for plotting
df["OverallAvg_s"] = df["OverallAvg_mmss"].apply(mmss_to_seconds)
df["NightAvg_s"]   = df["NightAvg_mmss"].apply(mmss_to_seconds)

# Baseline (0 stations) for deltas
baseline_overall_mmss = "04:48"
baseline_night_mmss   = "04:47"
baseline_overall_s = mmss_to_seconds(baseline_overall_mmss)
baseline_night_s   = mmss_to_seconds(baseline_night_mmss)

# ---------- UI ----------
st.set_page_config(page_title="Fire Cover Consultation Tool", layout="wide")
st.title("Fire Cover Consultation Tool")

st.markdown("Select how many stations would move from 24-hour to 12-hour operations and review the modelled impact below.")

stations = st.slider("Number of stations moving to 12-hour", 1, 11, 1)
row = df.loc[df["StationsMoved"] == stations].squeeze()

# ---------- Metrics ----------
st.subheader("Impact Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Yearly savings", f"£{row['YearlySavings']:,.2f}")
col2.metric("Overall response: avg time",
            row["OverallAvg_mmss"],
            delta=f"+{row['OverallImpact_s']} sec vs baseline ({baseline_overall_mmss})")
col3.metric("Night-time only: avg time",
            row["NightAvg_mmss"],
            delta=f"+{row['NightImpact_s']} sec vs baseline ({baseline_night_mmss})")
col4.metric("Reinvestment capacity (20-yr)", f"£{row['Invest_20yr_million']:.2f}m")

st.caption("Baseline is current modelled average: Overall **04:48**, Night-time **04:47**.")

# ---------- Narrative summary ----------
st.subheader("Scenario Summary")
st.info(
    f"Moving **{stations}** station(s) to 12-hour operation is modelled to save **£{row['YearlySavings']:,.0f} per year**. "
    f"Average brigade-wide attendance time increases by **{row['OverallImpact_s']} seconds** to **{row['OverallAvg_mmss']}**. "
    f"At night only, the increase is **{row['NightImpact_s']} seconds** to **{row['NightAvg_mmss']}**. "
    f"Across a 20-year asset life, cumulative efficiencies could enable **~£{row['Invest_20yr_million']:.2f}m** of investment."
)

# ---------- Charts ----------
st.subheader("How impacts change as more stations move")

# Response time lines
rt_long = df.melt(
    id_vars=["StationsMoved"],
    value_vars=["OverallAvg_s","NightAvg_s"],
    var_name="Series", value_name="Seconds"
).replace({"OverallAvg_s":"Overall avg", "NightAvg_s":"Night-time avg"})

fig_rt = px.line(
    rt_long, x="StationsMoved", y="Seconds", color="Series",
    markers=True, title="Modelled average attendance time by scenario"
)
fig_rt.update_yaxes(title="Seconds (mm:ss)", tickformat="%M:%S")
fig_rt.add_vline(x=stations, line_dash="dash")
st.plotly_chart(fig_rt, use_container_width=True)

# Investment line
fig_inv = px.line(
    df, x="StationsMoved", y="Invest_20yr_million", markers=True,
    title="Total reinvestment capacity over 20 years"
)
fig_inv.update_yaxes(title="£ million")
fig_inv.add_vline(x=stations, line_dash="dash")
st.plotly_chart(fig_inv, use_container_width=True)

# ---------- Data table & download ----------
with st.expander("See the full scenario table"):
    st.dataframe(df[[
        "StationsMoved","YearlySavings","OverallImpact_s","OverallAvg_mmss",
        "NightImpact_s","NightAvg_mmss","Invest_20yr_million"
    ]].rename(columns={
        "StationsMoved":"Stations moved",
        "YearlySavings":"Yearly savings (£)",
        "OverallImpact_s":"Overall impact (sec)",
        "OverallAvg_mmss":"Overall avg (mm:ss)",
        "NightImpact_s":"Night impact (sec)",
        "NightAvg_mmss":"Night avg (mm:ss)",
        "Invest_20yr_million":"Investment over 20 yrs (£m)"
    }), use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download scenario CSV", csv, file_name="fire_cover_scenarios.csv", mime="text/csv")

