# app/load_data.py
import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np
import glob


# ---- DB connection (Docker envs are already set in compose) ----
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "ukdata")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

ENGINE = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ---- Input CSV ----
CSV_PATH = "data/collisions_2023.csv"   # inside /app

# Columns we’ll keep -> map to our table schema
COLUMN_MAP = {
    "accident_index": "accident_index",
    "date": "accident_date",                 # DD/MM/YYYY
    "time": "accident_time",                 # HH:MM
    "latitude": "latitude",
    "longitude": "longitude",
    "accident_severity": "severity",
    "number_of_casualties": "number_of_casualties",
    "number_of_vehicles": "number_of_vehicles",
    "road_type": "road_type",
    "speed_limit": "speed_limit",
    "weather_conditions": "weather",
    "light_conditions": "light_conditions",
    "urban_or_rural_area": "urban_or_rural",
}


# Create table (if not exists)
CREATE_SQL = """
CREATE TABLE IF NOT EXISTS accidents (
  accident_index        TEXT PRIMARY KEY,
  accident_date         DATE,
  accident_time         TIME,
  latitude              DOUBLE PRECISION,
  longitude             DOUBLE PRECISION,
  severity              SMALLINT,
  number_of_casualties  SMALLINT,
  number_of_vehicles    SMALLINT,
  road_type             TEXT,
  speed_limit           SMALLINT,
  weather               TEXT,
  light_conditions      TEXT,
  urban_or_rural        TEXT,
  raw_json              JSONB
);
CREATE INDEX IF NOT EXISTS ix_accidents_date ON accidents (accident_date);
CREATE INDEX IF NOT EXISTS ix_accidents_severity ON accidents (severity);
"""

def tidy_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """Select, rename, and type-cast one chunk."""
    raw = df.replace({np.nan: None}).to_dict(orient="records")
    df["raw_json"] = [json.dumps(r) for r in raw]

    df = df[[c for c in COLUMN_MAP.keys() if c in df.columns]].copy()
    df = df.rename(columns=COLUMN_MAP)

    # Convert date/time (UK format)
    if "accident_date" in df.columns:
        df["accident_date"] = pd.to_datetime(
            df["accident_date"], dayfirst=True, errors="coerce"
        ).dt.date

    if "accident_time" in df.columns:
        df["accident_time"] = pd.to_datetime(
            df["accident_time"], format="%H:%M", errors="coerce"
        ).dt.time



    # Cast numeric-ish fields
    for col in ["latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["severity", "number_of_casualties", "number_of_vehicles", "speed_limit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df["raw_json"] = [json.dumps(r) for r in raw]
    return df

def main():
    files = sorted(glob.glob(DATA_GLOB))  # e.g. 2019…2023
    if not files:
        print("No files found under", DATA_GLOB)
        return

    total_rows = 0
    for path in files:
        print(f"\n=== Loading {os.path.basename(path)} ===")
        per_file = 0
        for chunk in pd.read_csv(path, chunksize=chunksize, low_memory=False, dtype=str, encoding="utf-8"):
            df = tidy_chunk(chunk)

            with ENGINE.begin() as conn:
                df.to_sql("_accidents_stage", con=conn, if_exists="replace", index=False)
                conn.execute(text("""
                    INSERT INTO accidents (
                        accident_index, accident_date, accident_time,
                        latitude, longitude, severity,
                        number_of_casualties, number_of_vehicles,
                        road_type, speed_limit, weather, light_conditions,
                        urban_or_rural, raw_json
                    )
                    SELECT
                        accident_index, accident_date, accident_time,
                        latitude, longitude, severity,
                        number_of_casualties, number_of_vehicles,
                        road_type, speed_limit, weather, light_conditions,
                        urban_or_rural, raw_json::jsonb
                    FROM _accidents_stage
                    ON CONFLICT (accident_index) DO NOTHING;

                    DROP TABLE _accidents_stage;
                """))

            per_file += len(df)
            total_rows += len(df)
            if per_file % 50000 == 0:
                print(f"Inserted {per_file:,} rows into DB from {os.path.basename(path)}...")
        print(f"✔ Finished {os.path.basename(path)} — inserted ~{per_file:,} rows (after dedupe).")

    print(f"\n✅ Data load complete. Total rows processed (pre-dedupe): {total_rows:,}")

if __name__ == "__main__":
    main()
