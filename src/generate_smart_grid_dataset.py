import numpy as np
import csv
import os
import time
from datetime import date

t0 = time.time()
np.random.seed(42)
OUT = "/home/claude/data"
os.makedirs(OUT, exist_ok=True)

def log(msg):
    print(f"[{time.time()-t0:6.1f}s] {msg}")

def rand_dates_str(start, end, n):
    s, e = date(*start).toordinal(), date(*end).toordinal()
    ords = np.random.randint(s, e, size=n)
    return np.array([date.fromordinal(int(o)).isoformat() for o in ords])

def write_csv(path, header, columns):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(zip(*columns))

# ---------- 1. UTILITY_PROVIDER (5) ----------
n = 5
provider_ids = np.array([f"UP-{i+1:04d}" for i in range(n)])
provider_names = np.array(["Meridian Power", "BlueRiver Energy", "Northgate Utilities",
                            "Solara Grid Co", "Cascade Electric"])
provider_regions = np.array(["Northeast", "Midwest", "Southeast", "Southwest", "Pacific"])
write_csv(f"{OUT}/01_utility_providers.csv",
          ["provider_id", "name", "region"],
          [provider_ids, provider_names, provider_regions])
log(f"utility_providers: {n} rows")

# ---------- 2. POWER_PLANT (50) ----------
n = 50
plant_ids = np.array([f"PP-{i+1:06d}" for i in range(n)])
plant_provider = np.random.choice(provider_ids, n)
plant_type = np.random.choice(["Coal", "Natural Gas", "Nuclear", "Hydro", "Solar Farm", "Wind Farm"], n,
                               p=[0.15, 0.30, 0.10, 0.15, 0.15, 0.15])
plant_capacity = np.round(np.random.uniform(50, 1500, n), 1)
write_csv(f"{OUT}/02_power_plants.csv",
          ["plant_id", "provider_id", "type", "capacity_mw"],
          [plant_ids, plant_provider, plant_type, plant_capacity])
log(f"power_plants: {n} rows")

# ---------- 3. RENEWABLE_SOURCE (300) ----------
n = 300
renewable_ids = np.array([f"RS-{i+1:06d}" for i in range(n)])
renewable_type = np.random.choice(["Solar PV", "Wind", "Biomass", "Small Hydro"], n, p=[0.45, 0.35, 0.1, 0.1])
renewable_output = np.round(np.random.uniform(50, 5000, n), 1)
write_csv(f"{OUT}/03_renewable_sources.csv",
          ["source_id", "type", "output_kw"],
          [renewable_ids, renewable_type, renewable_output])
log(f"renewable_sources: {n} rows")

# ---------- 4. ENERGY_STORAGE (150) ----------
n = 150
storage_ids = np.array([f"ES-{i+1:06d}" for i in range(n)])
storage_type = np.random.choice(["Li-ion BESS", "Flow Battery", "Flywheel"], n, p=[0.75, 0.15, 0.1])
storage_capacity = np.round(np.random.uniform(100, 20000, n), 1)
write_csv(f"{OUT}/04_energy_storage.csv",
          ["storage_id", "type", "capacity_kwh"],
          [storage_ids, storage_type, storage_capacity])
log(f"energy_storage: {n} rows")

# ---------- 5. SCADA_DMS (10) ----------
n = 10
scada_ids = np.array([f"SD-{i+1:04d}" for i in range(n)])
scada_provider = np.repeat(provider_ids, 2)
scada_function = np.tile(["SCADA", "DMS"], 5)
scada_center = np.array([f"{p.split('-')[1]}-Control-{f}" for p, f in zip(scada_provider, scada_function)])
write_csv(f"{OUT}/05_scada_dms.csv",
          ["system_id", "provider_id", "function", "control_center"],
          [scada_ids, scada_provider, scada_function, scada_center])
log(f"scada_dms: {n} rows")

# ---------- 6. SUBSTATION (2,000) ----------
n = 2000
substation_ids = np.array([f"SS-{i+1:07d}" for i in range(n)])
substation_type = np.random.choice(["Transmission", "Distribution"], n, p=[0.2, 0.8])
substation_location = np.array([f"Zone-{np.random.randint(1, 400)}" for _ in range(n)])
substation_voltage = np.where(substation_type == "Transmission",
                               np.random.choice([115, 230, 345, 500], n),
                               np.random.choice([4, 12, 25, 34.5], n))
src_type = np.random.choice(["POWER_PLANT", "RENEWABLE_SOURCE", "ENERGY_STORAGE"], n, p=[0.6, 0.25, 0.15])
src_id = np.empty(n, dtype=object)
src_id[src_type == "POWER_PLANT"] = np.random.choice(plant_ids, (src_type == "POWER_PLANT").sum())
src_id[src_type == "RENEWABLE_SOURCE"] = np.random.choice(renewable_ids, (src_type == "RENEWABLE_SOURCE").sum())
src_id[src_type == "ENERGY_STORAGE"] = np.random.choice(storage_ids, (src_type == "ENERGY_STORAGE").sum())
substation_scada = np.random.choice(scada_ids, n)
write_csv(f"{OUT}/06_substations.csv",
          ["substation_id", "substation_type", "location", "voltage_kv", "source_type", "source_id", "scada_id"],
          [substation_ids, substation_type, substation_location, substation_voltage, src_type, src_id, substation_scada])
log(f"substations: {n} rows")

# ---------- 7. POWER_TRANSFORMER (4,000) ----------
n = 4000
pt_ids = np.array([f"PT-{i+1:07d}" for i in range(n)])
pt_substation = np.random.choice(substation_ids, n)
pt_capacity = np.round(np.random.uniform(10, 500, n), 1)
write_csv(f"{OUT}/07_power_transformers.csv",
          ["transformer_id", "substation_id", "capacity_mva"],
          [pt_ids, pt_substation, pt_capacity])
log(f"power_transformers: {n} rows")

# ---------- 8. DISTRIBUTION_NETWORK (10,000) ----------
n = 10000
dn_ids = np.array([f"DN-{i+1:07d}" for i in range(n)])
dn_substation = np.random.choice(substation_ids, n)
dn_feeder_type = np.random.choice(["Overhead", "Underground"], n, p=[0.65, 0.35])
dn_scada = np.random.choice(scada_ids, n)
write_csv(f"{OUT}/08_distribution_networks.csv",
          ["network_id", "substation_id", "feeder_type", "scada_id"],
          [dn_ids, dn_substation, dn_feeder_type, dn_scada])
log(f"distribution_networks: {n} rows")

# ---------- 9. DISTRIBUTION_TRANSFORMER (500,000) ----------
n = 500_000
dt_ids = np.array([f"DT-{i+1:07d}" for i in range(n)])
dt_network = np.random.choice(dn_ids, n)
dt_rated_kva = np.random.choice([25, 37.5, 50, 75, 100, 167, 250], n)
write_csv(f"{OUT}/09_distribution_transformers.csv",
          ["transformer_id", "network_id", "rated_kva"],
          [dt_ids, dt_network, dt_rated_kva])
log(f"distribution_transformers: {n} rows")

# ---------- 10. DATA_MGMT_SYSTEM (5) ----------
n = 5
mdms_ids = np.array([f"MD-{i+1:04d}" for i in range(n)])
mdms_provider = provider_ids.copy()
mdms_storage = np.random.choice(["Cloud-Distributed", "On-Prem Cluster"], n)
mdms_analytics = np.random.choice(["VEE + Load Forecasting", "VEE + Billing Analytics"], n)
write_csv(f"{OUT}/10_data_mgmt_systems.csv",
          ["system_id", "provider_id", "storage_type", "analytics_engine"],
          [mdms_ids, mdms_provider, mdms_storage, mdms_analytics])
log(f"data_mgmt_systems: {n} rows")

# ---------- 11. AMI_HEAD_END (200) ----------
n = 200
hes_ids = np.array([f"HE-{i+1:04d}" for i in range(n)])
hes_network_type = np.random.choice(["RF Mesh", "Cellular (LTE-M)", "PLC"], n, p=[0.55, 0.3, 0.15])
hes_coverage = np.array([f"Coverage-Area-{i+1}" for i in range(n)])
hes_dms = np.random.choice(mdms_ids, n)
write_csv(f"{OUT}/11_ami_head_ends.csv",
          ["hes_id", "network_type", "coverage_area", "dms_system_id"],
          [hes_ids, hes_network_type, hes_coverage, hes_dms])
log(f"ami_head_ends: {n} rows")

# ---------- 12 & 13. CONSUMER + SMART_METER (10,000,000 each, generated together for true 1:1) ----------
N = 10_000_000
CHUNK = 1_000_000
account_types = ["Residential", "Commercial", "Industrial"]
account_p = [0.82, 0.15, 0.03]
comm_protocols = ["RF_MESH", "CELLULAR", "PLC"]
comm_p = [0.6, 0.25, 0.15]
streets = ["Oak", "Maple", "Elm", "Cedar", "Pine", "Birch", "River", "Highland", "Sunset", "Meadow"]
cities = ["Fairview", "Riverton", "Kingsford", "Bristow", "Ashland", "Milbrook", "Clearwater", "Greenfield"]
states = ["NY", "OH", "GA", "TX", "CA", "WA", "IL", "PA"]

cons_path = f"{OUT}/12_consumers.csv"
meter_path = f"{OUT}/13_smart_meters.csv"

with open(cons_path, "w", newline="") as fc, open(meter_path, "w", newline="") as fm:
    wc = csv.writer(fc)
    wm = csv.writer(fm)
    wc.writerow(["consumer_id", "account_type", "address"])
    wm.writerow(["meter_id", "transformer_id", "consumer_id", "hes_id",
                 "install_date", "reading_date", "comm_protocol"])

    n_chunks = N // CHUNK
    for c in range(n_chunks):
        start = c * CHUNK
        idx = np.arange(start, start + CHUNK)

        consumer_id = np.array([f"CN-{i+1:08d}" for i in idx])
        acct = np.random.choice(account_types, CHUNK, p=account_p)
        num = np.random.randint(100, 9999, CHUNK)
        street = np.random.choice(streets, CHUNK)
        city = np.random.choice(cities, CHUNK)
        st = np.random.choice(states, CHUNK)
        zipc = np.random.randint(10000, 99999, CHUNK)
        address = np.array([f"{n} {s} St, {ci}, {stt} {z}" for n, s, ci, stt, z in
                             zip(num, street, city, st, zipc)])
        wc.writerows(zip(consumer_id, acct, address))

        meter_id = np.array([f"SM-{i+1:08d}" for i in idx])
        transformer_id = np.random.choice(dt_ids, CHUNK)
        hes_id = np.random.choice(hes_ids, CHUNK)
        install_date = rand_dates_str((2015, 1, 1), (2023, 12, 31), CHUNK)
        reading_date = rand_dates_str((2026, 6, 1), (2026, 7, 30), CHUNK)
        protocol = np.random.choice(comm_protocols, CHUNK, p=comm_p)
        wm.writerows(zip(meter_id, transformer_id, consumer_id, hes_id,
                          install_date, reading_date, protocol))

        log(f"consumers+smart_meters chunk {c+1}/{n_chunks} written")

log("DONE")
