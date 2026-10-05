import pandas as pd
import requests

# Configuración del servidor OpenProject
BASE_URL = "http://3.17.144.120:8080"
API_ENDPOINT = f"{BASE_URL}/api/v3/users"
API_KEY = "c18adca153148f5886efc5fc1499ddedda02cbfcd6b8c90e23658137516a12bf"  # Sustituye por tu clave API token de OpenProject

# Cargar el archivo CSV adjunto
csv_file = "./data/openproject-xaldigital-spacexal-users.csv"
df = pd.read_csv(csv_file)

# OpenProject API v3 requiere Autenticación Básica HTTP utilizando el usuario 'apikey' y la clave como password
headers = {"Content-Type": "application/json"}
auth = ("apikey", API_KEY)

print(f"Iniciando la inserción de {len(df)} usuarios...")

for index, row in df.iterrows():
    # Estructura del objeto JSON según API v3 de OpenProject
    payload = {
        "login": str(row["Login"]).strip(),
        "firstName": str(row["First name"]).strip(),
        "lastName": str(row["Last name"]).strip(),
        "email": str(row["Email"]).strip(),
        "admin": bool(row["Admin"] == 1),
        "status": str(row["Status"]).strip().lower(),
        "language": str(row["Language"]).strip().lower(),
        "password": str(row["Password"]).strip(),
    }

    response = requests.post(
        API_ENDPOINT, json=payload, headers=headers, auth=auth
    )

    if response.status_code in [200, 201]:
        print(
            f"[✓] Usuario '{payload['login']}' ({payload['email']}) creado con éxito."
        )
    else:
        print(
            f"[✗] Error al crear '{payload['login']}': {response.status_code} - {response.text}"
        )