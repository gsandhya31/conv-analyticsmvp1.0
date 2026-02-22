"""
Generate 6 months of daily operations data for 30 fuel stations.
Date range: 2025-07-01 to 2025-12-31
Inserts directly into Supabase via REST API.
"""

import random
import json
from datetime import date, timedelta
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

random.seed(42)  # reproducible data

# Station configs: base volumes, types, EV capability
# Format: (station_id, station_type, has_ev, storage_capacity_kl, status)
STATIONS = [
    ("JBP-MH-001", "City", True, 80, "Active"),
    ("JBP-MH-002", "City", False, 60, "Active"),
    ("JBP-MH-003", "Highway", True, 120, "Active"),
    ("JBP-MH-004", "City", False, 50, "Active"),
    ("JBP-MH-005", "Highway", False, 100, "Active"),
    ("JBP-GJ-001", "City", True, 90, "Active"),
    ("JBP-GJ-002", "City", False, 55, "Active"),
    ("JBP-GJ-003", "Highway", True, 110, "Active"),
    ("JBP-DL-001", "City", True, 70, "Active"),
    ("JBP-DL-002", "City", False, 65, "Active"),
    ("JBP-DL-003", "Highway", True, 130, "Active"),
    ("JBP-RJ-001", "City", False, 60, "Active"),
    ("JBP-RJ-002", "Highway", False, 95, "Active"),
    ("JBP-UP-001", "City", False, 55, "Active"),
    ("JBP-UP-002", "Highway", False, 105, "Under Maintenance"),  # no data
    ("JBP-KA-001", "City", True, 85, "Active"),
    ("JBP-KA-002", "Highway", False, 100, "Active"),
    ("JBP-KA-003", "Semi-Urban", False, 45, "Active"),
    ("JBP-TN-001", "City", True, 75, "Active"),
    ("JBP-TN-002", "Highway", False, 95, "Active"),
    ("JBP-TS-001", "City", True, 80, "Active"),
    ("JBP-TS-002", "Highway", False, 90, "Active"),
    ("JBP-WB-001", "City", True, 70, "Active"),
    ("JBP-WB-002", "Highway", False, 100, "Active"),
    ("JBP-WB-003", "Semi-Urban", False, 40, "Active"),
    ("JBP-OD-001", "City", False, 55, "Active"),
    ("JBP-OD-002", "Highway", False, 85, "Active"),
    ("JBP-BR-001", "City", False, 50, "Active"),
    ("JBP-BR-002", "Highway", False, 75, "Inactive"),  # no data
]

# Base daily volumes by station type (liters)
BASE_VOLUMES = {
    "Highway":    {"Petrol": (3000, 5000), "Diesel": (5000, 9000)},
    "City":       {"Petrol": (2000, 4000), "Diesel": (1500, 3000)},
    "Semi-Urban": {"Petrol": (1000, 2000), "Diesel": (800, 1500)},
}

# Approximate prices per liter
PRICES = {"Petrol": 105.0, "Diesel": 92.0}

# Base footfall by station type
BASE_FOOTFALL = {
    "Highway": (400, 700),
    "City": (500, 900),
    "Semi-Urban": (200, 400),
}

START_DATE = date(2025, 7, 1)
END_DATE = date(2025, 12, 31)


def month_index(d):
    """Returns 0-5 for Jul-Dec 2025"""
    return (d.year - 2025) * 12 + d.month - 7


def generate_station_data(station_id, station_type, has_ev, storage_kl, status):
    """Generate all daily rows for one station."""
    if status in ("Under Maintenance", "Inactive"):
        return []

    rows = []
    storage_liters = storage_kl * 1000
    # Track closing stock per fuel type
    closing_stock = {
        "Petrol": storage_liters * 0.35,  # 70% total split roughly
        "Diesel": storage_liters * 0.35,
    }
    days_since_delivery = {"Petrol": 0, "Diesel": 0}

    current = START_DATE
    while current <= END_DATE:
        is_weekend = current.weekday() >= 5
        mi = month_index(current)
        # 2-3% monthly growth factor
        growth = 1.0 + (mi * 0.025)

        # Footfall (shared across fuel types, one value per day)
        base_ff = random.randint(*BASE_FOOTFALL[station_type])
        if is_weekend:
            weekend_mult = 1.25 if station_type == "Highway" else 1.17
            base_ff = int(base_ff * weekend_mult)
        footfall = int(base_ff * growth)

        # Safety incidents: 0 most days
        safety = 0
        r = random.random()
        if r < 0.04:      # ~4% chance of 1 incident
            safety = 1
        elif r < 0.008:    # ~0.8% chance of 2
            safety = 2

        # EV sessions
        ev_sessions = 0
        if has_ev:
            ev_base = random.randint(5, 20)
            ev_sessions = int(ev_base * (1.0 + mi * 0.08))  # EV growing faster

        # Dispenser downtime
        downtime = 0.0
        if random.random() < 0.08:  # 8% chance
            downtime = round(random.uniform(0.5, 4.0), 2)

        # Operating hours
        if station_type == "Highway":
            op_hours = random.choice([22.0, 23.0, 24.0])
        elif station_type == "City":
            op_hours = random.choice([18.0, 19.0, 20.0])
        else:
            op_hours = random.choice([16.0, 17.0, 18.0])

        for fuel_type in ["Petrol", "Diesel"]:
            vol_range = BASE_VOLUMES[station_type][fuel_type]
            base_vol = random.uniform(*vol_range)

            if is_weekend:
                weekend_mult = 1.25 if station_type == "Highway" else 1.17
                base_vol *= weekend_mult

            volume = round(base_vol * growth, 2)
            revenue = round(volume * PRICES[fuel_type] * random.uniform(0.97, 1.03), 2)

            # Stock management
            days_since_delivery[fuel_type] += 1
            stock_received = 0.0
            if days_since_delivery[fuel_type] >= random.randint(3, 5) or closing_stock[fuel_type] < storage_liters * 0.15:
                stock_received = round(random.uniform(0.4, 0.6) * storage_liters, 2)
                days_since_delivery[fuel_type] = 0

            new_stock = closing_stock[fuel_type] - volume + stock_received
            if new_stock < 0:
                stock_received += abs(new_stock) + storage_liters * 0.2
                new_stock = closing_stock[fuel_type] - volume + stock_received
            closing_stock[fuel_type] = round(new_stock, 2)

            rows.append({
                "station_id": station_id,
                "operation_date": current.isoformat(),
                "fuel_type": fuel_type,
                "volume_sold_liters": volume,
                "revenue_inr": revenue,
                "footfall": footfall,
                "safety_incidents": safety,
                "ev_charging_sessions": ev_sessions if fuel_type == "Petrol" else 0,  # count once
                "stock_received_liters": stock_received,
                "closing_stock_liters": closing_stock[fuel_type],
                "dispenser_downtime_hours": downtime,
                "operating_hours": op_hours,
            })

        current += timedelta(days=1)

    return rows


def main():
    all_rows = []
    for sid, stype, has_ev, cap, status in STATIONS:
        station_rows = generate_station_data(sid, stype, has_ev, cap, status)
        all_rows.extend(station_rows)
        print(f"  {sid}: {len(station_rows)} rows")

    print(f"\nTotal rows to insert: {len(all_rows)}")

    # Insert in batches of 500
    batch_size = 500
    for i in range(0, len(all_rows), batch_size):
        batch = all_rows[i:i + batch_size]
        result = supabase.table("daily_operations").insert(batch).execute()
        print(f"  Inserted batch {i // batch_size + 1} ({len(batch)} rows)")

    print("\nDone! All data inserted.")

    # Quick verification
    count = supabase.table("daily_operations").select("id", count="exact").execute()
    print(f"Total rows in daily_operations: {count.count}")


if __name__ == "__main__":
    main()
