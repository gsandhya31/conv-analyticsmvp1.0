# Jio-bp Fuel Station Analytics — Schema & Sample Data

## Overview

Two tables modeling Jio-bp's fuel retail operations across India. Data is synthetic but realistic in structure, volumes, and relationships.

---

## Table 1: fuel_stations (Master Data)

### Schema

```sql
CREATE TABLE fuel_stations (
    station_id VARCHAR(10) PRIMARY KEY,          -- e.g., 'JBP-MH-001'
    station_name VARCHAR(100) NOT NULL,          -- e.g., 'Jio-bp Andheri East'
    city VARCHAR(50) NOT NULL,                   -- e.g., 'Mumbai'
    state VARCHAR(50) NOT NULL,                  -- e.g., 'Maharashtra'
    region VARCHAR(20) NOT NULL,                 -- 'West', 'North', 'South', 'East'
    station_type VARCHAR(20) NOT NULL,           -- 'Highway', 'City', 'Semi-Urban'
    fuel_types_available TEXT[] NOT NULL,         -- {'Petrol', 'Diesel', 'EV Charging'}
    has_ev_charging BOOLEAN DEFAULT FALSE,       -- whether station has EV charging
    has_convenience_store BOOLEAN DEFAULT FALSE,  -- whether station has a c-store
    storage_capacity_kl NUMERIC(10,2),           -- total fuel storage in kiloliters
    num_dispensers INTEGER,                      -- number of fuel dispensers
    commissioned_date DATE,                      -- when station started operations
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6),
    status VARCHAR(20) DEFAULT 'Active'          -- 'Active', 'Under Maintenance', 'Inactive'
);
```

### Column Business Context

| Column | What Ops Team Cares About |
|--------|--------------------------|
| station_id | Unique identifier, format: JBP-{state code}-{number} |
| region | Jio-bp operates across 4 regions — used for regional performance comparison |
| station_type | Highway stations have higher diesel volume, city stations have higher petrol + footfall |
| has_ev_charging | Jio-bp is expanding EV infra — CEO has highlighted this |
| storage_capacity_kl | Determines reorder frequency and stockout risk |
| num_dispensers | Throughput capacity — bottleneck indicator |
| status | Active stations only should be included in performance metrics unless specified |

### Sample Data (30 stations)

```sql
INSERT INTO fuel_stations VALUES
-- West Region (Maharashtra, Gujarat)
('JBP-MH-001', 'Jio-bp Andheri East', 'Mumbai', 'Maharashtra', 'West', 'City', ARRAY['Petrol','Diesel','EV Charging'], true, true, 80.00, 8, '2023-01-15', 19.1197, 72.8464, 'Active'),
('JBP-MH-002', 'Jio-bp Pune Hinjewadi', 'Pune', 'Maharashtra', 'West', 'City', ARRAY['Petrol','Diesel'], false, true, 60.00, 6, '2023-03-10', 18.5913, 73.7389, 'Active'),
('JBP-MH-003', 'Jio-bp Mumbai-Pune Expressway', 'Lonavala', 'Maharashtra', 'West', 'Highway', ARRAY['Petrol','Diesel','EV Charging'], true, true, 120.00, 12, '2023-02-01', 18.7557, 73.4091, 'Active'),
('JBP-MH-004', 'Jio-bp Navi Mumbai Vashi', 'Navi Mumbai', 'Maharashtra', 'West', 'City', ARRAY['Petrol','Diesel'], false, false, 50.00, 5, '2023-06-20', 19.0771, 72.9987, 'Active'),
('JBP-MH-005', 'Jio-bp Nashik Highway', 'Nashik', 'Maharashtra', 'West', 'Highway', ARRAY['Petrol','Diesel'], false, true, 100.00, 10, '2023-04-15', 20.0063, 73.7808, 'Active'),
('JBP-GJ-001', 'Jio-bp Ahmedabad SG Highway', 'Ahmedabad', 'Gujarat', 'West', 'City', ARRAY['Petrol','Diesel','EV Charging'], true, true, 90.00, 9, '2023-01-20', 23.0225, 72.5714, 'Active'),
('JBP-GJ-002', 'Jio-bp Surat Ring Road', 'Surat', 'Gujarat', 'West', 'City', ARRAY['Petrol','Diesel'], false, false, 55.00, 6, '2023-07-01', 21.1702, 72.8311, 'Active'),
('JBP-GJ-003', 'Jio-bp Ahmedabad-Vadodara Expressway', 'Anand', 'Gujarat', 'West', 'Highway', ARRAY['Petrol','Diesel','EV Charging'], true, true, 110.00, 11, '2023-05-10', 22.5645, 72.9289, 'Active'),

-- North Region (Delhi NCR, Rajasthan, UP)
('JBP-DL-001', 'Jio-bp Dwarka Sector 21', 'New Delhi', 'Delhi', 'North', 'City', ARRAY['Petrol','Diesel','EV Charging'], true, true, 70.00, 7, '2023-02-15', 28.5563, 77.0561, 'Active'),
('JBP-DL-002', 'Jio-bp Noida Sector 62', 'Noida', 'Uttar Pradesh', 'North', 'City', ARRAY['Petrol','Diesel'], false, true, 65.00, 7, '2023-04-01', 28.6273, 77.3654, 'Active'),
('JBP-DL-003', 'Jio-bp Gurugram NH-48', 'Gurugram', 'Haryana', 'North', 'Highway', ARRAY['Petrol','Diesel','EV Charging'], true, true, 130.00, 14, '2023-01-10', 28.4595, 77.0266, 'Active'),
('JBP-RJ-001', 'Jio-bp Jaipur Tonk Road', 'Jaipur', 'Rajasthan', 'North', 'City', ARRAY['Petrol','Diesel'], false, false, 60.00, 6, '2023-05-20', 26.8656, 75.8127, 'Active'),
('JBP-RJ-002', 'Jio-bp Jaipur-Ajmer Highway', 'Ajmer', 'Rajasthan', 'North', 'Highway', ARRAY['Petrol','Diesel'], false, true, 95.00, 9, '2023-06-15', 26.4499, 74.6399, 'Active'),
('JBP-UP-001', 'Jio-bp Lucknow Gomti Nagar', 'Lucknow', 'Uttar Pradesh', 'North', 'City', ARRAY['Petrol','Diesel'], false, false, 55.00, 5, '2023-08-01', 26.8508, 80.9915, 'Active'),
('JBP-UP-002', 'Jio-bp Agra-Lucknow Expressway', 'Kanpur', 'Uttar Pradesh', 'North', 'Highway', ARRAY['Petrol','Diesel'], false, true, 105.00, 10, '2023-03-25', 26.4499, 80.3319, 'Under Maintenance'),

-- South Region (Karnataka, Tamil Nadu, Telangana)
('JBP-KA-001', 'Jio-bp Bangalore Whitefield', 'Bangalore', 'Karnataka', 'South', 'City', ARRAY['Petrol','Diesel','EV Charging'], true, true, 85.00, 8, '2023-01-25', 12.9698, 77.7500, 'Active'),
('JBP-KA-002', 'Jio-bp Bangalore-Mysore Highway', 'Mandya', 'Karnataka', 'South', 'Highway', ARRAY['Petrol','Diesel'], false, true, 100.00, 10, '2023-04-10', 12.5227, 76.8952, 'Active'),
('JBP-KA-003', 'Jio-bp Hubli', 'Hubli', 'Karnataka', 'South', 'Semi-Urban', ARRAY['Petrol','Diesel'], false, false, 45.00, 4, '2023-09-01', 15.3647, 75.1240, 'Active'),
('JBP-TN-001', 'Jio-bp Chennai OMR', 'Chennai', 'Tamil Nadu', 'South', 'City', ARRAY['Petrol','Diesel','EV Charging'], true, true, 75.00, 7, '2023-02-20', 12.9165, 80.2270, 'Active'),
('JBP-TN-002', 'Jio-bp Chennai-Bangalore Highway', 'Vellore', 'Tamil Nadu', 'South', 'Highway', ARRAY['Petrol','Diesel'], false, true, 95.00, 9, '2023-05-05', 12.9165, 79.1325, 'Active'),
('JBP-TS-001', 'Jio-bp Hyderabad HITEC City', 'Hyderabad', 'Telangana', 'South', 'City', ARRAY['Petrol','Diesel','EV Charging'], true, true, 80.00, 8, '2023-03-15', 17.4486, 78.3908, 'Active'),
('JBP-TS-002', 'Jio-bp Hyderabad-Vijayawada NH-65', 'Suryapet', 'Telangana', 'South', 'Highway', ARRAY['Petrol','Diesel'], false, false, 90.00, 8, '2023-07-10', 17.1383, 79.6367, 'Active'),

-- East Region (West Bengal, Odisha, Bihar)
('JBP-WB-001', 'Jio-bp Kolkata Salt Lake', 'Kolkata', 'West Bengal', 'East', 'City', ARRAY['Petrol','Diesel','EV Charging'], true, true, 70.00, 7, '2023-03-01', 22.5805, 88.4168, 'Active'),
('JBP-WB-002', 'Jio-bp Kolkata-Durgapur Expressway', 'Burdwan', 'West Bengal', 'East', 'Highway', ARRAY['Petrol','Diesel'], false, true, 100.00, 10, '2023-06-01', 23.2332, 87.8615, 'Active'),
('JBP-WB-003', 'Jio-bp Siliguri', 'Siliguri', 'West Bengal', 'East', 'Semi-Urban', ARRAY['Petrol','Diesel'], false, false, 40.00, 4, '2023-10-01', 26.7271, 88.3953, 'Active'),
('JBP-OD-001', 'Jio-bp Bhubaneswar NH-16', 'Bhubaneswar', 'Odisha', 'East', 'City', ARRAY['Petrol','Diesel'], false, false, 55.00, 5, '2023-05-15', 20.2961, 85.8245, 'Active'),
('JBP-OD-002', 'Jio-bp Cuttack Highway', 'Cuttack', 'Odisha', 'East', 'Highway', ARRAY['Petrol','Diesel'], false, true, 85.00, 8, '2023-08-10', 20.4625, 85.8830, 'Active'),
('JBP-BR-001', 'Jio-bp Patna Bailey Road', 'Patna', 'Bihar', 'East', 'City', ARRAY['Petrol','Diesel'], false, false, 50.00, 5, '2023-07-20', 25.6093, 85.1376, 'Active'),
('JBP-BR-002', 'Jio-bp Patna-Gaya NH-83', 'Gaya', 'Bihar', 'East', 'Highway', ARRAY['Petrol','Diesel'], false, false, 75.00, 7, '2023-09-15', 24.7955, 85.0002, 'Inactive');
```

---

## Table 2: daily_operations (Transactional Data)

### Schema

```sql
CREATE TABLE daily_operations (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(10) REFERENCES fuel_stations(station_id),
    operation_date DATE NOT NULL,
    fuel_type VARCHAR(20) NOT NULL,              -- 'Petrol', 'Diesel'
    volume_sold_liters NUMERIC(12,2),            -- liters sold that day for that fuel type
    revenue_inr NUMERIC(14,2),                   -- revenue in INR
    footfall INTEGER,                            -- total customer visits (not per fuel type)
    safety_incidents INTEGER DEFAULT 0,          -- number of safety incidents reported
    ev_charging_sessions INTEGER DEFAULT 0,      -- EV charging sessions (0 if no EV at station)
    stock_received_liters NUMERIC(12,2) DEFAULT 0, -- fuel received from tanker delivery
    closing_stock_liters NUMERIC(12,2),          -- end-of-day fuel inventory
    dispenser_downtime_hours NUMERIC(5,2) DEFAULT 0, -- hours dispensers were non-functional
    operating_hours NUMERIC(4,1) DEFAULT 18.0,   -- hours station was open (typically 18-24)

    UNIQUE(station_id, operation_date, fuel_type)
);

-- Index for common query patterns
CREATE INDEX idx_ops_date ON daily_operations(operation_date);
CREATE INDEX idx_ops_station_date ON daily_operations(station_id, operation_date);
CREATE INDEX idx_ops_region_date ON daily_operations(station_id, operation_date, fuel_type);
```

### Column Business Context

| Column | What Ops Team Cares About |
|--------|--------------------------|
| fuel_type | Petrol vs Diesel split is a key metric. Diesel dominates highway stations. |
| volume_sold_liters | Primary performance metric. Compared across stations, regions, time. |
| revenue_inr | Petrol ~₹105/liter, Diesel ~₹92/liter approximately. Revenue = volume × price. |
| footfall | Shared across fuel types per station per day. Indicator of station traffic. |
| safety_incidents | Critical KPI — CEO highlighted safety. Spikes need investigation. |
| ev_charging_sessions | Growing metric — Jio-bp expanding EV. Only at stations with has_ev_charging=true. |
| stock_received_liters | Tanker deliveries. Irregular (every 2-5 days depending on station). |
| closing_stock_liters | Low closing stock = stockout risk. Key for supply chain planning. |
| dispenser_downtime_hours | Maintenance/reliability indicator. High downtime = lost revenue. |

### Data Generation Logic

Generate 6 months of data (2025-07-01 to 2025-12-31) for all 30 stations, both Petrol and Diesel. This gives ~10,800 rows.

Use this Python script to generate realistic data:

```python
import random
from datetime import date, timedelta

# Base volumes per station type (liters/day per fuel type)
BASE_VOLUMES = {
    ('Highway', 'Diesel'): (8000, 15000),    # Highway = high diesel
    ('Highway', 'Petrol'): (4000, 8000),
    ('City', 'Diesel'): (3000, 6000),
    ('City', 'Petrol'): (5000, 10000),       # City = high petrol
    ('Semi-Urban', 'Diesel'): (2000, 4000),
    ('Semi-Urban', 'Petrol'): (2000, 4000),
}

# Price ranges (INR per liter) — slight variation by state
PRICES = {
    'Petrol': (103.0, 107.0),
    'Diesel': (90.0, 94.0),
}

# Footfall ranges per station type (daily, shared across fuel types)
FOOTFALL = {
    'Highway': (300, 800),
    'City': (400, 1200),
    'Semi-Urban': (150, 400),
}

# Data generation rules:
# - Weekend volumes ~15-20% higher for city, ~25% higher for highway
# - Safety incidents: 0 most days, occasional 1, rare 2+ (avg ~0.8/station/month)
# - EV sessions: only for has_ev_charging stations, 5-30/day, growing trend
# - Stock received: every 3-5 days, roughly matching consumption
# - Closing stock: track inventory (start at 70% capacity, adjust daily)
# - Dispenser downtime: 0 most days, occasional 1-4 hours
# - Inactive/Under Maintenance stations: no data during those periods
# - Month-over-month growth: ~2-3% volume increase to show trending
```

**IMPORTANT:** When building, generate this data via a Python script and insert into Supabase. Don't ask Claude to write 10,800 INSERT statements. Generate a CSV or use batch insert.

---

## NL→SQL System Prompt Template

Use this as the system prompt when calling Claude API for SQL generation:

```
You are a SQL query generator for Jio-bp's fuel station operations analytics system.

You have access to a PostgreSQL database with the following tables:

TABLE: fuel_stations
- station_id (VARCHAR, PK) — format JBP-{state}-{number}, e.g. 'JBP-MH-001'
- station_name (VARCHAR) — human-readable name
- city (VARCHAR)
- state (VARCHAR) — Indian state
- region (VARCHAR) — one of: 'West', 'North', 'South', 'East'
- station_type (VARCHAR) — one of: 'Highway', 'City', 'Semi-Urban'
- fuel_types_available (TEXT[]) — array, e.g. {'Petrol', 'Diesel', 'EV Charging'}
- has_ev_charging (BOOLEAN)
- has_convenience_store (BOOLEAN)
- storage_capacity_kl (NUMERIC) — kiloliters
- num_dispensers (INTEGER)
- commissioned_date (DATE)
- latitude, longitude (NUMERIC)
- status (VARCHAR) — one of: 'Active', 'Under Maintenance', 'Inactive'

TABLE: daily_operations
- id (SERIAL, PK)
- station_id (VARCHAR, FK → fuel_stations)
- operation_date (DATE)
- fuel_type (VARCHAR) — 'Petrol' or 'Diesel'
- volume_sold_liters (NUMERIC)
- revenue_inr (NUMERIC) — in Indian Rupees
- footfall (INTEGER) — daily customer visits, shared across fuel types
- safety_incidents (INTEGER) — 0 on most days
- ev_charging_sessions (INTEGER) — 0 if station has no EV charging
- stock_received_liters (NUMERIC) — tanker delivery, 0 on most days
- closing_stock_liters (NUMERIC)
- dispenser_downtime_hours (NUMERIC)
- operating_hours (NUMERIC) — typically 18-24

UNIQUE constraint: (station_id, operation_date, fuel_type)

DATA RANGE: 2025-07-01 to 2025-12-31

RULES:
1. ONLY generate SELECT queries. Never INSERT, UPDATE, DELETE, DROP, or ALTER.
2. Always filter for status = 'Active' stations unless the user specifically asks about inactive/maintenance stations.
3. Use table aliases (fs for fuel_stations, do for daily_operations).
4. For date references: "last month" = most recent complete month in data, "this quarter" = most recent quarter, etc. The latest date in data is 2025-12-31.
5. When asked about "sales" or "volume", default to volume_sold_liters unless revenue is specifically mentioned.
6. footfall is per station per day (not per fuel type). Don't double-count when joining with daily_operations which has 2 rows per station per day (petrol + diesel). Use DISTINCT or subqueries.
7. If the question is ambiguous, make reasonable assumptions and state them.
8. If the question cannot be answered from these tables, say so clearly.
9. Return valid PostgreSQL syntax.
10. LIMIT results to 20 rows unless the user asks for more.

RESPOND IN THIS EXACT JSON FORMAT:
{
  "sql": "SELECT ...",
  "explanation": "One-line plain English explanation of what this query does",
  "assumptions": ["assumption 1", "assumption 2"]
}

If the question cannot be answered:
{
  "sql": null,
  "explanation": "This question cannot be answered from the available data because...",
  "assumptions": []
}
```

---

## Sample Q&A Pairs (Include 4 in the NL→SQL Prompt as Few-Shot Examples)

**Q: "Which region has the highest diesel sales this quarter?"**
```json
{
  "sql": "SELECT fs.region, SUM(do.volume_sold_liters) as total_diesel_liters FROM daily_operations do JOIN fuel_stations fs ON do.station_id = fs.station_id WHERE do.fuel_type = 'Diesel' AND do.operation_date >= '2025-10-01' AND fs.status = 'Active' GROUP BY fs.region ORDER BY total_diesel_liters DESC LIMIT 5",
  "explanation": "Sums diesel volume sold per region for Q4 2025 (Oct-Dec), ranked highest first.",
  "assumptions": ["'This quarter' interpreted as Q4 2025 (Oct-Dec) based on available data range"]
}
```

**Q: "Top 5 stations by revenue last month"**
```json
{
  "sql": "SELECT fs.station_name, fs.city, fs.region, SUM(do.revenue_inr) as total_revenue FROM daily_operations do JOIN fuel_stations fs ON do.station_id = fs.station_id WHERE do.operation_date >= '2025-12-01' AND do.operation_date <= '2025-12-31' AND fs.status = 'Active' GROUP BY fs.station_id, fs.station_name, fs.city, fs.region ORDER BY total_revenue DESC LIMIT 5",
  "explanation": "Shows top 5 stations by total revenue (petrol + diesel) for December 2025.",
  "assumptions": ["'Last month' = December 2025, the most recent complete month"]
}
```

**Q: "Average daily footfall — highway vs city stations"**
```json
{
  "sql": "SELECT fs.station_type, ROUND(AVG(sub.daily_footfall)) as avg_daily_footfall FROM (SELECT DISTINCT do.station_id, do.operation_date, do.footfall as daily_footfall FROM daily_operations do) sub JOIN fuel_stations fs ON sub.station_id = fs.station_id WHERE fs.station_type IN ('Highway', 'City') AND fs.status = 'Active' GROUP BY fs.station_type",
  "explanation": "Compares average daily footfall between highway and city stations, avoiding double-counting from the petrol/diesel rows.",
  "assumptions": ["Excludes Semi-Urban stations as the question only asks about Highway vs City"]
}
```

**Q: "How many safety incidents in Maharashtra last 3 months?"**
```json
{
  "sql": "SELECT COUNT(*) as total_incidents, SUM(do.safety_incidents) as incident_count FROM daily_operations do JOIN fuel_stations fs ON do.station_id = fs.station_id WHERE fs.state = 'Maharashtra' AND do.operation_date >= '2025-10-01' AND do.safety_incidents > 0 AND fs.status = 'Active'",
  "explanation": "Counts total safety incidents across all Maharashtra stations for Oct-Dec 2025.",
  "assumptions": ["'Last 3 months' = October to December 2025"]
}
```
