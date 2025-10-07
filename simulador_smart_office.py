#!/usr/bin/env python3
"""
simulador_smart_office.py
Gera um dataset simulado de sensores para um "Smart Office".
Registros: 7 dias, intervalo de 15 minutos.
Sensores: temperature (°C), luminosity (lux), occupancy (0/1).
Salva: smart_office_data.csv
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate(start_date="2025-09-30", days=7, freq_minutes=15, seed=42):
    start = datetime.fromisoformat(start_date)
    periods = days * 24 * (60 // freq_minutes)
    rng = np.random.default_rng(seed=seed)

    temp_sensors = [f"temp_{i+1}" for i in range(3)]
    light_sensors = [f"light_{i+1}" for i in range(3)]
    occ_sensors = [f"occ_{i+1}" for i in range(5)]
    all_sensors = [("temperature", s) for s in temp_sensors] + \\
                  [("luminosity", s) for s in light_sensors] + \\
                  [("occupancy", s) for s in occ_sensors]

    rows = []
    for i in range(periods):
        ts = start + timedelta(minutes=i * freq_minutes)
        hour = ts.hour
        weekday = ts.weekday()
        temp_base = 20 + 4 * (1 / (1 + np.exp(-0.5 * (hour - 8)))) * (1 / (1 + np.exp(0.5 * (hour - 18))))
        light_base = 0
        if 7 <= hour <= 18:
            light_base = 100 + 900 * np.sin(np.pi * (hour - 7) / 11)
        if weekday < 5 and 8 <= hour < 18:
            occ_prob_base = 0.7
        else:
            occ_prob_base = 0.05

        for sensor_type, sensor_id in all_sensors:
            if sensor_type == "temperature":
                noise = rng.normal(0, 0.5)
                drift = (rng.normal(0, 0.1) if (i % (24*4) == 0) else 0)
                value = round(temp_base + noise + drift, 2)
                if rng.random() < 0.001:
                    value += rng.choice([-5, 5])
            elif sensor_type == "luminosity":
                noise = rng.normal(0, 10)
                value = max(0, round(light_base + noise + rng.normal(0, 20), 1))
                if rng.random() < 0.002:
                    value += rng.integers(300, 1200)
            else:
                sensor_factor = 1.0 if int(sensor_id.split(\"_\")[1]) <= 3 else 0.6
                prob = min(1.0, occ_prob_base * sensor_factor + rng.normal(0, 0.05))
                occupied = 1 if rng.random() < prob else 0
                if weekday >= 5 and rng.random() < 0.01:
                    occupied = 1
                value = occupied

            rows.append({
                "timestamp": ts.isoformat(sep=' '),
                "sensor_type": sensor_type,
                "sensor_id": sensor_id,
                "value": value
            })

    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = generate(start_date="2025-09-30", days=7, freq_minutes=15, seed=42)
    df.to_csv("smart_office_data.csv", index=False)
    print("Arquivo smart_office_data.csv gerado com sucesso.")
