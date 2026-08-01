import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURACIÓN DE RUTAS ABSOLUTAS ---
OS_DIR = '/app/data_lakehouse'
if not os.path.exists(OS_DIR):
    os.makedirs(OS_DIR)

GRID_FILE = os.path.join(OS_DIR, 'smart_grids_10m.csv')
METER_FILE = os.path.join(OS_DIR, 'smart_meters_10m.csv')
MAP_TEMP_FILE = os.path.join(OS_DIR, 'substation_geo_map.csv')

TOTAL_ROWS = 10000000
CHUNK_SIZE = 500000  # Procesamiento seguro de RAM para evitar caídas del contenedor

# Geografía Completa (8 Países y sus Regiones/Ciudades Reales)
GEOGRAPHY = {
    'United States': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'Colombia': ['Bogota', 'Medellin', 'Cali', 'Barranquilla', 'Cartagena'],
    'Mexico': ['Mexico City', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana'],
    'Brasil': ['Sao Paulo', 'Rio de Janeiro', 'Brasilia', 'Salvador', 'Fortaleza'],
    'Spain': ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Zaragoza'],
    'Netherlands': ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven'],
    'Germany': ['Berlin', 'Munich', 'Frankfurt', 'Hamburg', 'Cologne'],
    'China': ['Shanghai', 'Beijing', 'Guangzhou', 'Shenzhen', 'Chengdu']
}
countries_list = list(GEOGRAPHY.keys())

# Pools de Infraestructura del Sector Eléctrico
SUBSTATION_POOL = [f"SUB-{np.random.randint(1000, 9999)}" for _ in range(500)]
# Pool controlado a 50,000 para garantizar series temporales densas (>5 registros por medidor)
METER_POOL = [f"MTR-{np.random.randint(1000000, 9999999)}" for _ in range(50000)]

# Intervalos de días permitidos para simular ciclos de facturación mensuales estrictos
BILLING_DAYS = np.array([30, 31])

# Limpieza inicial de archivos residuales
for f in [GRID_FILE, METER_FILE, MAP_TEMP_FILE]:
    if os.path.exists(f):
        os.remove(f)

base_date = datetime(2026, 7, 30)
num_chunks = TOTAL_ROWS // CHUNK_SIZE


# ==============================================================================
# --- FASE 1: SMART GRID INFRASTRUCTURE (Generación del Maestro Padre) ---
# ==============================================================================
print(f"Iniciando Fase 1: Generando Smart Grids primero (Estructura de Red)...")

for i in range(num_chunks):
    start_row = i * CHUNK_SIZE
    print(f"de-platform | Smart Grid | Bloque {i+1}/{num_chunks}...")
    
    g_countries = np.random.choice(countries_list, CHUNK_SIZE)
    g_cities = [np.random.choice(GEOGRAPHY[c]) for c in g_countries]
    
    # Simulación estricta de intervalos mensuales retrocediendo en el tiempo
    g_months_back = (np.arange(start_row, start_row + CHUNK_SIZE) % 24)
    g_chosen_intervals = np.random.choice(BILLING_DAYS, CHUNK_SIZE)
    g_days_back = g_months_back * g_chosen_intervals
    g_dates = [base_date - timedelta(days=int(d)) for d in g_days_back]
    
    chunk_substations = np.random.choice(SUBSTATION_POOL, CHUNK_SIZE)

    load_mw = np.random.uniform(50.0, 2500.0, size=CHUNK_SIZE)
    renew_mw = load_mw * np.random.uniform(0.0, 0.60, size=CHUNK_SIZE)
    
    grid_df = pd.DataFrame({
        'substation_id': chunk_substations,
        'country': g_countries,
        'city': g_cities,
        'reading_date': g_dates,
        'active_load_mw': np.round(load_mw, 2),
        'renewable_generation_mw': np.round(renew_mw, 2),
        'bus_voltage_kv': np.round(np.random.normal(loc=115.0, scale=1.1, size=CHUNK_SIZE), 1),
        'grid_frequency_hz': np.round(np.random.normal(loc=60.0, scale=0.012, size=CHUNK_SIZE), 3),
        'thd_pct': np.round(np.random.exponential(scale=1.1, size=CHUNK_SIZE) + 0.3, 2),
        'locational_marginal_price_mwh': np.round(np.random.normal(loc=55.0, scale=20.0, size=CHUNK_SIZE), 2),
        'grid_stability_index': np.round(np.random.uniform(0.90, 1.0, size=CHUNK_SIZE), 3),
        'breaker_status': np.random.choice(['CLOSED', 'OPEN'], CHUNK_SIZE, p=[0.9993, 0.0007])
    })
    grid_df.to_csv(GRID_FILE, mode='a', index=False, header=not os.path.exists(GRID_FILE))
    
    # Extraer y guardar relaciones válidas (Padre) para que los medidores (Hijos) las hereden en la Fase 2
    geo_map_chunk = grid_df[['substation_id', 'country', 'city', 'reading_date']].drop_duplicates()
    geo_map_chunk.to_csv(MAP_TEMP_FILE, mode='a', index=False, header=not os.path.exists(MAP_TEMP_FILE))


# ==============================================================================
# --- FASE 2: SMART METERS (Hijos dependientes vinculados de forma estricta) ---
# ==============================================================================
print(f"\nIniciando Fase 2: Cargando mapa estructural para heredar relaciones...")

# Cargar el dataframe mapeador para forzar la consistencia referencial
network_map = pd.read_csv(MAP_TEMP_FILE)
if os.path.exists(MAP_TEMP_FILE):
    os.remove(MAP_TEMP_FILE)  # Limpieza inmediata de memoria interna

print(f"Generando Smart Meters a partir de la infraestructura existente...")

for i in range(num_chunks):
    print(f"de-platform | Smart Meters | Bloque {i+1}/{num_chunks}...")
    
    # Muestrear directamente del mapa padre para heredar Subestación, País, Ciudad y Fecha exactas
    network_sample = network_map.sample(n=CHUNK_SIZE, replace=True).reset_index(drop=True)
    
    active_kwh = np.random.exponential(scale=210.0, size=CHUNK_SIZE)
    pf = np.random.uniform(0.85, 0.99, size=CHUNK_SIZE)
    
    meter_df = pd.DataFrame({
        'meter_id': np.random.choice(METER_POOL, CHUNK_SIZE),  # Reutiliza IDs para construir series históricas densas
        'substation_id': network_sample['substation_id'],     # INTEGRIDAD REFERENCIAL 1:N PERFECTA
        'country': network_sample['country'],                 # Ubicación coherente con el nodo
        'city': network_sample['city'],                       # Ubicación coherente con el nodo
        'reading_date': network_sample['reading_date'],       # Historial con saltos estrictos de 30 o 31 días
        'active_power_kwh': np.round(active_kwh, 3),
        'reactive_power_kvarh': np.round(active_kwh * np.tan(np.arccos(pf)), 3),
        'power_factor': np.round(pf, 2),
        'peak_demand_kw': np.round((active_kwh / 30) * np.random.uniform(1.2, 1.8, CHUNK_SIZE), 2),
        'tariff_rate_code': np.random.choice(['TOU-PRIME', 'RES-STANDARD', 'COMM-DEMAND'], CHUNK_SIZE),
        'temperature_c': np.round(np.random.normal(loc=22.0, scale=7.0, size=CHUNK_SIZE), 1),
        'tamper_alert': np.random.choice([0, 1], CHUNK_SIZE, p=[0.9994, 0.0006])
    })
    meter_df.to_csv(METER_FILE, mode='a', index=False, header=not os.path.exists(METER_FILE))

print(f"\n¡Generación completada con éxito estricto! Archivos listos en: {OS_DIR}/")
