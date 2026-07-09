"""
US Airline Flight Delays (2014-2018) - interactive Streamlit dashboard.

Runs entirely off small pre-computed summary tables in aggregates/ (built
from ~30M raw BTS flight records by scripts/build_aggregates.py), so the app
is fast and deployable even though the raw data is 3.5 GB.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="US Airline Delays 2014-2018", page_icon="✈️",
                   layout="wide")

HERE = os.path.dirname(os.path.abspath(__file__))
AGG = os.path.join(HERE, "aggregates")

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DOW_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
CANCEL_REASONS = {"A": "Carrier", "B": "Weather", "C": "NAS", "D": "Security"}
CAUSE_LABELS = {"carrier_min": "Carrier", "weather_min": "Weather",
                "nas_min": "NAS (air system)", "security_min": "Security",
                "late_aircraft_min": "Late aircraft"}


@st.cache_data
def load():
    t = {name: pd.read_csv(os.path.join(AGG, f"{name}.csv"))
         for name in ["monthly_carrier", "airport_stats", "dow_month_heatmap",
                      "hourly", "routes", "cancellation_codes",
                      "airlines_lookup", "airports_lookup"]}
    t["airlines_lookup"].columns = ["code", "airline"]
    return t


try:
    T = load()
except FileNotFoundError:
    st.error("Aggregates not found. Run `python scripts/build_aggregates.py` "
             "first (requires the raw BTS CSVs in Data/).")
    st.stop()

mc = T["monthly_carrier"].merge(T["airlines_lookup"], left_on="OP_CARRIER",
                                right_on="code", how="left")
mc["airline"] = mc["airline"].fillna(mc["OP_CARRIER"])

# ─── Sidebar filters (everything updates live) ───────────────────────────
st.sidebar.header("✈️ Filters")
years = st.sidebar.multiselect("Years", sorted(mc["year"].unique()),
                               default=sorted(mc["year"].unique()))
all_airlines = sorted(mc["airline"].unique())
airlines = st.sidebar.multiselect("Airlines (empty = all)", all_airlines)

view = mc[mc["year"].isin(years)]
if airlines:
    view = view[view["airline"].isin(airlines)]

if view.empty:
    st.warning("No data for this selection - pick at least one year.")
    st.stop()

# ─── Header KPIs ─────────────────────────────────────────────────────────
st.title("✈️ US Airline Flight Delays (2014-2018)")
st.caption(f"{view['flights'].sum():,.0f} flights in view · aggregated from "
           f"~30M BTS records")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Flights", f"{view['flights'].sum() / 1e6:,.1f}M")
k2.metric("Delayed 15+ min", f"{view['delayed15'].sum() / view['flights'].sum():.1%}")
k3.metric("Avg departure delay",
          f"{view['dep_delay_sum'].sum() / view['dep_delay_n'].sum():.1f} min")
k4.metric("Cancelled", f"{view['cancelled'].sum() / view['flights'].sum():.2%}")
k5.metric("Avg taxi-out + taxi-in",
          f"{(view['taxi_out_sum'].sum() + view['taxi_in_sum'].sum()) / view['dep_delay_n'].sum():.0f} min")

tab_trend, tab_air, tab_apt, tab_when, tab_cause = st.tabs(
    ["📈 Trends", "🛩 Airlines", "🛫 Airports & Routes",
     "🗓 When to Fly", "🔍 Delay Causes"])


# ─── Tab 1: trends ───────────────────────────────────────────────────────
with tab_trend:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Monthly flight volume")
        vol = (view.groupby(["year", "month"])["flights"].sum().reset_index())
        vol["date"] = pd.to_datetime(vol[["year", "month"]].assign(day=1))
        st.line_chart(vol.set_index("date")["flights"], height=280)
    with c2:
        st.subheader("Share of flights delayed 15+ min")
        d = view.groupby(["year", "month"]).agg(
            delayed15=("delayed15", "sum"), flights=("flights", "sum")).reset_index()
        d["pct_delayed"] = d["delayed15"] / d["flights"]
        pivot = d.pivot(index="month", columns="year", values="pct_delayed")
        pivot.index = [MONTH_NAMES[m - 1] for m in pivot.index]
        fig, ax = plt.subplots(figsize=(7, 4.2))
        pivot.plot(ax=ax, marker="o")
        ax.set_ylabel("% delayed 15+ min")
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
        ax.grid(alpha=0.3)
        ax.legend(title="Year", ncol=3, fontsize=8)
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Year over year")
    yoy = view.groupby("year").agg(
        flights=("flights", "sum"), delayed15=("delayed15", "sum"),
        cancelled=("cancelled", "sum"),
        dep_delay_sum=("dep_delay_sum", "sum"),
        dep_delay_n=("dep_delay_n", "sum")).reset_index()
    yoy["% delayed"] = (yoy["delayed15"] / yoy["flights"]).map("{:.1%}".format)
    yoy["% cancelled"] = (yoy["cancelled"] / yoy["flights"]).map("{:.2%}".format)
    yoy["avg dep delay (min)"] = (yoy["dep_delay_sum"] / yoy["dep_delay_n"]).round(1)
    yoy["flights"] = yoy["flights"].map("{:,.0f}".format)
    st.dataframe(yoy[["year", "flights", "% delayed", "% cancelled",
                      "avg dep delay (min)"]], width="stretch", hide_index=True)


# ─── Tab 2: airlines ─────────────────────────────────────────────────────
with tab_air:
    by_air = view.groupby("airline").agg(
        flights=("flights", "sum"), delayed15=("delayed15", "sum"),
        cancelled=("cancelled", "sum"),
        arr_delay_sum=("arr_delay_sum", "sum"),
        arr_delay_n=("arr_delay_n", "sum")).reset_index()
    by_air["pct_delayed"] = by_air["delayed15"] / by_air["flights"]
    by_air["avg_arr_delay"] = by_air["arr_delay_sum"] / by_air["arr_delay_n"]
    by_air = by_air.sort_values("pct_delayed")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Delay rate by airline")
        fig, ax = plt.subplots(figsize=(7, 6))
        colors = plt.cm.RdYlGn_r(by_air["pct_delayed"] / by_air["pct_delayed"].max())
        ax.barh(by_air["airline"], by_air["pct_delayed"], color=colors)
        ax.set_xlabel("% flights delayed 15+ min")
        ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
        st.pyplot(fig)
        plt.close(fig)
    with c2:
        st.subheader("Volume vs punctuality")
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.scatter(by_air["flights"] / 1e6, by_air["pct_delayed"],
                   s=by_air["cancelled"] / by_air["cancelled"].max() * 600 + 40,
                   alpha=0.6, c="#2c7fb8")
        for _, r in by_air.iterrows():
            ax.annotate(r["airline"].split()[0],
                        (r["flights"] / 1e6, r["pct_delayed"]), fontsize=7,
                        xytext=(4, 4), textcoords="offset points")
        ax.set_xlabel("Flights (millions)")
        ax.set_ylabel("% delayed 15+ min")
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
        ax.grid(alpha=0.3)
        ax.set_title("Bubble size = cancellations")
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Why flights get cancelled")
    cc = T["cancellation_codes"]
    cc = cc[cc["year"].isin(years)].merge(
        T["airlines_lookup"], left_on="OP_CARRIER", right_on="code", how="left")
    cc["airline"] = cc["airline"].fillna(cc["OP_CARRIER"])
    if airlines:
        cc = cc[cc["airline"].isin(airlines)]
    cc["reason"] = cc["CANCELLATION_CODE"].map(CANCEL_REASONS)
    pivot = (cc.groupby(["airline", "reason"])["count"].sum()
             .unstack(fill_value=0))
    if len(pivot):
        fig, ax = plt.subplots(figsize=(12, 4.5))
        pivot.plot.bar(stacked=True, ax=ax,
                       color=["#d62728", "#1f77b4", "#ff7f0e", "#2ca02c"])
        ax.set_ylabel("Cancelled flights")
        ax.set_xlabel("")
        plt.xticks(rotation=45, ha="right", fontsize=8)
        st.pyplot(fig)
        plt.close(fig)


# ─── Tab 3: airports & routes ────────────────────────────────────────────
with tab_apt:
    ap = T["airport_stats"]
    ap = ap[ap["year"].isin(years)].groupby("ORIGIN", as_index=False).sum(
        numeric_only=True)
    ap["pct_delayed"] = ap["delayed15"] / ap["flights"]
    ap["avg_dep_delay"] = ap["dep_delay_sum"] / ap["dep_delay_n"]
    ap = ap.merge(T["airports_lookup"], left_on="ORIGIN",
                  right_on="IATA_CODE", how="left")

    min_flights = st.slider("Minimum flights at airport", 1000, 200000, 50000,
                            1000)
    big = ap[ap["flights"] >= min_flights].copy()

    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("Departure delays across the US")
        mp = big.dropna(subset=["LATITUDE", "LONGITUDE"]).copy()
        fig, ax = plt.subplots(figsize=(9, 5.5))
        sc = ax.scatter(mp["LONGITUDE"], mp["LATITUDE"],
                        s=mp["flights"] / mp["flights"].max() * 500 + 10,
                        c=mp["pct_delayed"], cmap="RdYlGn_r", alpha=0.75,
                        edgecolors="grey", linewidths=0.3)
        ax.set_xlim(-130, -65)
        ax.set_ylim(23, 50)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Bubble size = flights · colour = % delayed")
        plt.colorbar(sc, ax=ax, label="% delayed",
                     format=lambda v, _: f"{v:.0%}")
        for _, r in mp.nlargest(8, "flights").iterrows():
            ax.annotate(r["ORIGIN"], (r["LONGITUDE"], r["LATITUDE"]),
                        fontsize=7, fontweight="bold")
        st.pyplot(fig)
        plt.close(fig)
    with c2:
        st.subheader("Worst on-time performance")
        worst = big.nlargest(12, "pct_delayed")[
            ["ORIGIN", "CITY", "flights", "pct_delayed", "avg_dep_delay"]].copy()
        worst["pct_delayed"] = worst["pct_delayed"].map("{:.1%}".format)
        worst["flights"] = worst["flights"].map("{:,.0f}".format)
        worst["avg_dep_delay"] = worst["avg_dep_delay"].round(1)
        st.dataframe(worst, width="stretch", hide_index=True, height=430)

    st.subheader("🔎 Route lookup")
    r = T["routes"]
    r = r[r["year"].isin(years)].groupby(["ORIGIN", "DEST"],
                                         as_index=False).sum(numeric_only=True)
    r["pct_delayed"] = r["delayed15"] / r["flights"]
    r["avg_arr_delay"] = r["arr_delay_sum"] / r["arr_delay_n"]
    c1, c2 = st.columns(2)
    origin = c1.selectbox("From", sorted(r["ORIGIN"].unique()),
                          index=sorted(r["ORIGIN"].unique()).index("JFK")
                          if "JFK" in r["ORIGIN"].values else 0)
    dests = sorted(r[r["ORIGIN"] == origin]["DEST"].unique())
    dest = c2.selectbox("To", dests)
    route = r[(r["ORIGIN"] == origin) & (r["DEST"] == dest)]
    if len(route):
        rr = route.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Flights on route", f"{rr['flights']:,.0f}")
        c2.metric("% delayed 15+", f"{rr['pct_delayed']:.1%}")
        c3.metric("Avg arrival delay", f"{rr['avg_arr_delay']:.1f} min")


# ─── Tab 4: when to fly ──────────────────────────────────────────────────
with tab_when:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Delay rate: month × day of week")
        hm = T["dow_month_heatmap"]
        hm = hm[hm["year"].isin(years)].groupby(["month", "dow"],
                                                as_index=False).sum(
            numeric_only=True)
        hm["pct"] = hm["delayed15"] / hm["flights"]
        grid = hm.pivot(index="month", columns="dow", values="pct")
        grid.index = [MONTH_NAMES[m - 1] for m in grid.index]
        grid.columns = [DOW_NAMES[d] for d in grid.columns]
        fig, ax = plt.subplots(figsize=(7, 5.5))
        sns.heatmap(grid, annot=True, fmt=".0%", cmap="RdYlGn_r",
                    cbar=False, ax=ax, annot_kws={"size": 8})
        ax.set_ylabel("")
        st.pyplot(fig)
        plt.close(fig)
        best = hm.loc[hm["pct"].idxmin()]
        worst = hm.loc[hm["pct"].idxmax()]
        st.caption(f"Best: **{DOW_NAMES[int(best['dow'])]}s in "
                   f"{MONTH_NAMES[int(best['month']) - 1]}** "
                   f"({best['pct']:.0%} delayed) · Worst: "
                   f"**{DOW_NAMES[int(worst['dow'])]}s in "
                   f"{MONTH_NAMES[int(worst['month']) - 1]}** "
                   f"({worst['pct']:.0%}).")
    with c2:
        st.subheader("Delays build through the day")
        hr = T["hourly"]
        hr = hr[hr["year"].isin(years)].groupby("dep_hour",
                                                as_index=False).sum(
            numeric_only=True)
        hr["avg_delay"] = hr["dep_delay_sum"] / hr["dep_delay_n"]
        hr["pct"] = hr["delayed15"] / hr["flights"]
        fig, ax = plt.subplots(figsize=(7, 5.5))
        ax.bar(hr["dep_hour"], hr["pct"], color="#fd8d3c", alpha=0.85)
        ax.set_xlabel("Scheduled departure hour")
        ax.set_ylabel("% delayed 15+ min")
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
        ax.set_xticks(range(0, 24, 2))
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)
        st.caption("Morning flights are the safest bet - delays compound "
                   "as late aircraft ripple through the day.")


# ─── Tab 5: delay causes ─────────────────────────────────────────────────
with tab_cause:
    cause_cols = list(CAUSE_LABELS)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Total delay minutes by cause")
        totals = view[cause_cols].sum().rename(CAUSE_LABELS).sort_values()
        fig, ax = plt.subplots(figsize=(7, 4.5))
        (totals / 1e6).plot.barh(ax=ax, color="#756bb1")
        ax.set_xlabel("Delay minutes (millions)")
        st.pyplot(fig)
        plt.close(fig)
    with c2:
        st.subheader("Cause mix by month")
        bym = view.groupby("month")[cause_cols].sum()
        bym.index = [MONTH_NAMES[m - 1] for m in bym.index]
        share = bym.div(bym.sum(axis=1), axis=0).rename(columns=CAUSE_LABELS)
        fig, ax = plt.subplots(figsize=(7, 4.5))
        share.plot.area(ax=ax, alpha=0.85, cmap="tab10")
        ax.set_ylabel("Share of delay minutes")
        ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
        ax.legend(fontsize=8, loc="lower left")
        ax.margins(x=0)
        st.pyplot(fig)
        plt.close(fig)
    st.info("**Late aircraft** and **carrier** issues drive most delay "
            "minutes - weather spikes in summer and winter, while security "
            "is negligible.")

st.divider()
st.caption("Data: US BTS On-Time Performance 2014-2018 · aggregates built by "
           "scripts/build_aggregates.py")
