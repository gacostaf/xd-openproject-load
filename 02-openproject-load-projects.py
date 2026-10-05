import os
import pandas as pd
import requests

# Configuración del servidor OpenProject
BASE_URL = "http://3.17.144.120:8080"
API_ENDPOINT = f"{BASE_URL}/api/v3/projects"
API_KEY = "c18adca153148f5886efc5fc1499ddedda02cbfcd6b8c90e23658137516a12bf"  # Reemplazar con la API Key del usuario Administrador

# Rutas de archivos
DATA_DIR = r"C:\Users\gerar\openproject-load\data"
CSV_FILE_PATH = os.path.join(DATA_DIR, "openproject-xaldigital-spacexal-projects.csv")

# Configuración de autenticación HTTP Basic
headers = {"Content-Type": "application/json"}
auth = ("apikey", API_KEY)

def create_projects():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"[✗] Error: No se encontró el archivo CSV en {CSV_FILE_PATH}")
        return

    print(f"Cargando archivo: {CSV_FILE_PATH}")
    df = pd.read_csv(CSV_FILE_PATH)

    print(f"Iniciando inserción de {len(df)} proyecto(s)...")

    for index, row in df.iterrows():
        # Construir payload para la API v3 de OpenProject
        payload = {
            "name": str(row["Name"]).strip(),
            "identifier": str(row["Identifier"]).strip().lower(),
            "public": bool(row["Public"]) if pd.notna(row.get("Public")) else False,
            "description": {
                "format": "markdown",
                "raw": str(row["Description"]).strip() if pd.notna(row.get("Description")) else ""
            }
        }

        # Manejo de Proyecto Padre si existe
        if "Parent" in row and pd.notna(row["Parent"]) and str(row["Parent"]).strip():
            payload["_links"] = {
                "parent": {
                    "href": f"/api/v3/projects/{str(row['Parent']).strip()}"
                }
            }

        response = requests.post(API_ENDPOINT, json=payload, headers=headers, auth=auth)

        if response.status_code in [200, 201]:
            print(f"[✓] Proyecto '{payload['name']}' ({payload['identifier']}) creado exitosamente.")
        else:
            print(f"[✗] Error al crear el proyecto '{payload['name']}': {response.status_code} - {response.text}")

if __name__ == "__main__":
    create_projects()