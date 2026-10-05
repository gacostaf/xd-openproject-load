import os
import requests
import pandas as pd

# --- CONFIGURACIÓN DE CONEXIÓN ---
API_URL = "http://3.17.144.120:8080"  # Cambia por la URL de tu instancia
API_KEY = "c18adca153148f5886efc5fc1499ddedda02cbfcd6b8c90e23658137516a12bf"        # Reemplaza por tu API Key de OpenProject
CSV_PATH = r"C:\Users\gerar\openproject-load\data\openproject-xaldigital-spacexal-members.csv"

auth = ("apikey", API_KEY)
headers = {"Content-Type": "application/json"}


def clean_str(val):
    """Limpia espacios y comillas especiales (curvas/rectas) del texto."""
    if pd.isna(val):
        return ""
    s = str(val).strip()
    for char in ['“', '”', '"', "'"]:
        s = s.replace(char, "")
    return s.strip()


def get_users_map():
    """Consulta la API y mapea: user_login.lower() -> user_id"""
    users_map = {}
    url = f"{API_URL}/api/v3/users?pageSize=500"
    resp = requests.get(url, auth=auth, headers=headers)
    
    if resp.status_code == 200:
        elements = resp.json().get("_embedded", {}).get("elements", [])
        for user in elements:
            login = clean_str(user.get("login")).lower()
            user_id = user.get("id")
            if login and user_id:
                users_map[login] = user_id
    else:
        print(f"[!] Error al obtener usuarios de la API ({resp.status_code}): {resp.text}")
        
    return users_map


def get_roles_map():
    """Consulta la API y mapea: role_name.lower() -> role_id"""
    roles_map = {}
    url = f"{API_URL}/api/v3/roles"
    resp = requests.get(url, auth=auth, headers=headers)
    
    if resp.status_code == 200:
        elements = resp.json().get("_embedded", {}).get("elements", [])
        for role in elements:
            role_name = clean_str(role.get("name")).lower()
            role_id = role.get("id")
            if role_name and role_id:
                roles_map[role_name] = role_id
    else:
        print(f"[!] Error al obtener roles de la API ({resp.status_code}): {resp.text}")
        
    return roles_map


def get_projects_map():
    """Consulta la API y mapea: project_identifier.lower() -> project_id"""
    projects_map = {}
    url = f"{API_URL}/api/v3/projects?pageSize=500"
    resp = requests.get(url, auth=auth, headers=headers)
    
    if resp.status_code == 200:
        elements = resp.json().get("_embedded", {}).get("elements", [])
        for project in elements:
            identifier = clean_str(project.get("identifier")).lower()
            project_id = project.get("id")
            if identifier and project_id:
                projects_map[identifier] = project_id
    else:
        print(f"[!] Error al obtener proyectos de la API ({resp.status_code}): {resp.text}")
        
    return projects_map


def load_members():
    if not os.path.exists(CSV_PATH):
        print(f"[✗] No se encontró el archivo CSV en: {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)

    print("[i] Consultando mapas de IDs desde OpenProject...")
    users_map = get_users_map()
    roles_map = get_roles_map()
    projects_map = get_projects_map()

    print(f" -> Usuarios encontrados en servidor: {len(users_map)}")
    print(f" -> Proyectos encontrados en servidor: {len(projects_map)}")
    print(f" -> Roles disponibles en servidor: {roles_map}\n")

    for idx, row in df.iterrows():
        project_ident = clean_str(row.get("ProjectIdentifier")).lower()
        user_login = clean_str(row.get("UserLogin")).lower()
        role_name = clean_str(row.get("Role")).lower()

        project_id = projects_map.get(project_ident)
        user_id = users_map.get(user_login)
        role_id = roles_map.get(role_name)

        # Validación de existencias antes de hacer la petición POST
        if not project_id:
            print(f"[✗] Fila {idx + 1}: El proyecto '{project_ident}' no existe en OpenProject.")
            continue
        if not user_id:
            print(f"[✗] Fila {idx + 1}: El usuario '{user_login}' no existe en OpenProject.")
            continue
        if not role_id:
            print(f"[✗] Fila {idx + 1}: El rol '{role_name}' no existe en OpenProject.")
            continue

        # Estructura JSON requerida por /api/v3/memberships
        payload = {
            "_links": {
                "project": {"href": f"/api/v3/projects/{project_id}"},
                "principal": {"href": f"/api/v3/users/{user_id}"},
                "roles": [{"href": f"/api/v3/roles/{role_id}"}]
            }
        }

        url = f"{API_URL}/api/v3/memberships"
        res = requests.post(url, auth=auth, headers=headers, json=payload)

        if res.status_code in [200, 201]:
            print(f"[✓] Éxito: '{user_login}' asignado a '{project_ident}' con rol '{role_name}' (ID: {role_id})")
        else:
            print(f"[✗] Error al asignar '{user_login}' en '{project_ident}': {res.status_code} - {res.text}")


if __name__ == "__main__":
    load_members()