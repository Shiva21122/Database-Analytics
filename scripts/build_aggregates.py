"""
US Airline Delays - aggregation pipeline.

Reduces ~30M raw BTS flight records (2014-2018, ~3.5 GB, NOT in GitHub) into
small summary tables in aggregates/ (a few hundred KB, committed to GitHub)
that power the Streamlit dashboard (app.py).

Run once from the project root:  python scripts/build_aggregates.py
Runtime: several minutes (streams each yearly CSV in 1M-row chunks).
"""

import glob
import os

import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(HERE, "Data")
OUT_DIR = os.path.join(HERE, "aggregates")
os.makedirs(OUT_DIR, exist_ok=True)

USECOLS = [
    "FL_DATE", "OP_CARRIER", "ORIGIN", "DEST", "CRS_DEP_TIME",
    "DEP_DELAY", "TAXI_OUT", "TAXI_IN", "ARR_DELAY",
    "CANCELLED", "CANCELLATION_CODE", "DIVERTED",
    "CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY",
    "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY",
]
CAUSE_COLS = ["CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY",
              "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]

monthly, airports, heatmap, hourly, routes, cancels = [], [], [], [], [], []


def process_chunk(chunk):
    chunk["FL_DATE"] = pd.to_datetime(chunk["FL_DATE"], errors="coerce")
    chunk = chunk.dropna(subset=["FL_DATE"])
    chunk["year"] = chunk["FL_DATE"].dt.year
    chunk["month"] = chunk["FL_DATE"].dt.month
    chunk["dow"] = chunk["FL_DATE"].dt.dayofweek
    chunk["dep_hour"] = (pd.to_numeric(chunk["CRS_DEP_TIME"], errors="coerce")
                         // 100).clip(0, 23)
    chunk["delayed15"] = (chunk["ARR_DELAY"] >= 15).astype(int)
    chunk["CANCELLED"] = chunk["CANCELLED"].fillna(0).astype(int)
    chunk["DIVERTED"] = chunk["DIVERTED"].fillna(0).astype(int)
    for c in CAUSE_COLS:
        chunk[c] = chunk[c].fillna(0)

    monthly.append(chunk.groupby(["year", "month", "OP_CARRIER"]).agg(
        flights=("FL_DATE", "size"),
        cancelled=("CANCELLED", "sum"),
        diverted=("DIVERTED", "sum"),
        delayed15=("delayed15", "sum"),
        dep_delay_sum=("DEP_DELAY", "sum"),
        dep_delay_n=("DEP_DELAY", "count"),
        arr_delay_sum=("ARR_DELAY", "sum"),
        arr_delay_n=("ARR_DELAY", "count"),
        taxi_out_sum=("TAXI_OUT", "sum"),
        taxi_in_sum=("TAXI_IN", "sum"),
        carrier_min=("CARRIER_DELAY", "sum"),
        weather_min=("WEATHER_DELAY", "sum"),
        nas_min=("NAS_DELAY", "sum"),
        security_min=("SECURITY_DELAY", "sum"),
        late_aircraft_min=("LATE_AIRCRAFT_DELAY", "sum"),
    ).reset_index())

    airports.append(chunk.groupby(["year", "ORIGIN"]).agg(
        flights=("FL_DATE", "size"),
        cancelled=("CANCELLED", "sum"),
        delayed15=("delayed15", "sum"),
        dep_delay_sum=("DEP_DELAY", "sum"),
        dep_delay_n=("DEP_DELAY", "count"),
    ).reset_index())

    heatmap.append(chunk.groupby(["year", "month", "dow"]).agg(
        flights=("FL_DATE", "size"),
        delayed15=("delayed15", "sum"),
        arr_delay_sum=("ARR_DELAY", "sum"),
        arr_delay_n=("ARR_DELAY", "count"),
    ).reset_index())

    hourly.append(chunk.groupby(["year", "dep_hour"]).agg(
        flights=("FL_DATE", "size"),
        delayed15=("delayed15", "sum"),
        dep_delay_sum=("DEP_DELAY", "sum"),
        dep_delay_n=("DEP_DELAY", "count"),
    ).reset_index())

    routes.append(chunk.groupby(["year", "ORIGIN", "DEST"]).agg(
        flights=("FL_DATE", "size"),
        delayed15=("delayed15", "sum"),
        arr_delay_sum=("ARR_DELAY", "sum"),
        arr_delay_n=("ARR_DELAY", "count"),
    ).reset_index())

    cx = chunk[chunk["CANCELLED"] == 1]
    if len(cx):
        cancels.append(cx.groupby(["year", "OP_CARRIER", "CANCELLATION_CODE"])
                       .size().rename("count").reset_index())


def combine(parts, keys, sums):
    df = pd.concat(parts, ignore_index=True)
    return df.groupby(keys, as_index=False)[sums].sum()


def main():
    files = sorted(glob.glob(os.path.join(RAW_DIR, "20*.csv")))
    if not files:
        raise FileNotFoundError(f"No yearly CSVs found in {RAW_DIR}")
    for path in files:
        print(f"Processing {os.path.basename(path)} ...", flush=True)
        for i, chunk in enumerate(pd.read_csv(path, usecols=USECOLS,
                                              chunksize=1_000_000,
                                              low_memory=False)):
            process_chunk(chunk)
            print(f"  chunk {i + 1} done", flush=True)

    specs = {
        "monthly_carrier.csv": (monthly, ["year", "month", "OP_CARRIER"]),
        "airport_stats.csv": (airports, ["year", "ORIGIN"]),
        "dow_month_heatmap.csv": (heatmap, ["year", "month", "dow"]),
        "hourly.csv": (hourly, ["year", "dep_hour"]),
        "routes.csv": (routes, ["year", "ORIGIN", "DEST"]),
        "cancellation_codes.csv": (cancels,
                                   ["year", "OP_CARRIER",
                                    "CANCELLATION_CODE"]),
    }
    for name, (parts, keys) in specs.items():
        df = pd.concat(parts, ignore_index=True)
        sums = [c for c in df.columns if c not in keys]
        out = df.groupby(keys, as_index=False)[sums].sum()
        # keep routes file small: only routes with 300+ flights per year
        if name == "routes.csv":
            out = out[out["flights"] >= 300]
        out.to_csv(os.path.join(OUT_DIR, name), index=False)
        print(f"Wrote {name}: {len(out):,} rows", flush=True)

    # copy small lookup tables next to the aggregates as plain CSV
    pd.read_excel(os.path.join(RAW_DIR, "US_Airlines.xlsx")).to_csv(
        os.path.join(OUT_DIR, "airlines_lookup.csv"), index=False)
    pd.read_excel(os.path.join(RAW_DIR, "US_Airports.xlsx")).to_csv(
        os.path.join(OUT_DIR, "airports_lookup.csv"), index=False)
    print("Done.")


if __name__ == "__main__":
    main()
