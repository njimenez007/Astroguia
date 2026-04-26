import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytz
import requests
from dotenv import load_dotenv

load_dotenv()

_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")
_OPENCAGE_KEY = os.getenv("OPENCAGE_API_KEY")

_PROKERALA_BASE = "https://api.prokerala.com"
_OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json"

# Lahiri (Chitra Paksha) — mismo ayanamsa que Parashara's Light
_AYANAMSA = 1


def _get_token() -> str:
    resp = requests.post(
        f"{_PROKERALA_BASE}/token",
        data={
            "grant_type": "client_credentials",
            "client_id": _CLIENT_ID,
            "client_secret": _CLIENT_SECRET,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _geocode(ciudad: str) -> dict:
    resp = requests.get(
        _OPENCAGE_URL,
        params={"q": ciudad, "key": _OPENCAGE_KEY, "limit": 1, "language": "es"},
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise ValueError(f"Ciudad no encontrada: '{ciudad}'")
    r = results[0]
    return {
        "lat": r["geometry"]["lat"],
        "lon": r["geometry"]["lng"],
        "timezone": r["annotations"]["timezone"]["name"],
    }


def _build_datetime(fecha: str, hora: str, timezone_name: str) -> str:
    tz = pytz.timezone(timezone_name)
    naive_dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    return tz.localize(naive_dt).isoformat()


def _call(endpoint: str, params: dict, token: str) -> dict:
    resp = requests.get(
        f"{_PROKERALA_BASE}/v2{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def get_birth_data(nombre: str, fecha: str, hora: str, ciudad: str) -> dict:
    """
    Obtiene todos los datos astrológicos védicos para la Carta Astral.

    Args:
        nombre: Nombre completo del consultante.
        fecha:  Fecha de nacimiento en formato YYYY-MM-DD.
        hora:   Hora de nacimiento en formato HH:MM (24 h).
        ciudad: Ciudad de nacimiento (ej: "Bogotá, Colombia").

    Returns:
        dict con datos_natales + secciones astrológicas listos para inyectar
        en los prompts maestros de AstroGuía.

    Endpoints reales disponibles en Prokerala API v2:
        - /astrology/birth-details   → Nakshatra, Rashi, Pada, Deidad
        - /astrology/kundli          → Carta natal + Doshas + Yogas básicos
        - /astrology/kundli/advanced → Yogas detallados + Vimshottari Dasha completo

    No disponibles en la API (requieren Parashara's Light para Dario):
        - Sade Sati, Ashtakavarga, Shadbala / Bhava Bala
    """
    geo = _geocode(ciudad)
    token = _get_token()
    datetime_str = _build_datetime(fecha, hora, geo["timezone"])

    base = {
        "ayanamsa": _AYANAMSA,
        "coordinates": f"{geo['lat']},{geo['lon']}",
        "datetime": datetime_str,
    }

    # 3 endpoints reales de Prokerala (en paralelo)
    calls = [
        ("birth_details",   "/astrology/birth-details",    {}),
        ("kundli",          "/astrology/kundli",            {}),
        ("kundli_advanced", "/astrology/kundli/advanced",   {}),
    ]

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_key = {
            executor.submit(_call, endpoint, {**base, **extra}, token): key
            for key, endpoint, extra in calls
        }
        for future in as_completed(future_to_key):
            key = future_to_key[future]
            results[key] = future.result()

    return {
        "nombre": nombre,
        "datos_natales": {
            "fecha": fecha,
            "hora": hora,
            "ciudad": ciudad,
            "latitud": geo["lat"],
            "longitud": geo["lon"],
            "timezone": geo["timezone"],
            "datetime_iso": datetime_str,
        },
        # Nakshatra de Luna, Sol y Ascendente — Pada, Deidad, Rashi
        "birth_details": results["birth_details"],
        # Carta natal básica + Mangal Dosha + Yogas (Dhana, Raja, etc.)
        "kundli": results["kundli"],
        # Yogas detallados + Vimshottari Dasha completo (Maha/Antar/Pratyantar)
        "kundli_advanced": results["kundli_advanced"],
        # Datos no disponibles en Prokerala API — calcular con Parashara's Light
        "_no_disponible_via_api": [
            "sade_sati",
            "ashtakavarga",
            "shadbala",
            "bhava_bala",
        ],
    }
