"""
AstroGuía — Motor de Cálculo Védico (Jyotish)
Motor propio · ephem + Python puro · Lahiri · Whole Sign · Geocéntrico

Nota: pyswisseph da True Node y Bhava Sripati exactos, pero necesita
Microsoft C++ Build Tools para compilarse en Windows. Este motor usa
ephem (posiciones idénticas a pyswisseph para objetos mayores) y
Nodo Medio para Rahu/Ketu (diferencia < 1° respecto al Nodo Verdadero).
"""
import os, math, json
from datetime import datetime, date, timedelta
from typing import Optional
import ephem
import pytz
from timezonefinder import TimezoneFinder
import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATOS ESTÁTICOS
# ─────────────────────────────────────────────────────────────────────────────

OPENCAGE_KEY = os.getenv("OPENCAGE_API_KEY")
TZF = TimezoneFinder()

SIGNOS = [
    {"id": 0, "nombre": "Aries",       "elem": "Fuego",  "cual": "Móvil",   "reg": "Marte"},
    {"id": 1, "nombre": "Tauro",       "elem": "Tierra", "cual": "Fijo",    "reg": "Venus"},
    {"id": 2, "nombre": "Géminis",     "elem": "Aire",   "cual": "Dual",    "reg": "Mercurio"},
    {"id": 3, "nombre": "Cáncer",      "elem": "Agua",   "cual": "Móvil",   "reg": "Luna"},
    {"id": 4, "nombre": "Leo",         "elem": "Fuego",  "cual": "Fijo",    "reg": "Sol"},
    {"id": 5, "nombre": "Virgo",       "elem": "Tierra", "cual": "Dual",    "reg": "Mercurio"},
    {"id": 6, "nombre": "Libra",       "elem": "Aire",   "cual": "Móvil",   "reg": "Venus"},
    {"id": 7, "nombre": "Escorpio",    "elem": "Agua",   "cual": "Fijo",    "reg": "Marte"},
    {"id": 8, "nombre": "Sagitario",   "elem": "Fuego",  "cual": "Dual",    "reg": "Júpiter"},
    {"id": 9, "nombre": "Capricornio", "elem": "Tierra", "cual": "Móvil",   "reg": "Saturno"},
    {"id": 10,"nombre": "Acuario",     "elem": "Aire",   "cual": "Fijo",    "reg": "Saturno"},
    {"id": 11,"nombre": "Piscis",      "elem": "Agua",   "cual": "Dual",    "reg": "Júpiter"},
]

NAKSHATRAS = [
    {"id": 1,  "nombre": "Ashwini",          "regente": "Ketu",     "deidad": "Ashvini Kumaras"},
    {"id": 2,  "nombre": "Bharani",          "regente": "Venus",    "deidad": "Yama"},
    {"id": 3,  "nombre": "Krittika",         "regente": "Sol",      "deidad": "Agni"},
    {"id": 4,  "nombre": "Rohini",           "regente": "Luna",     "deidad": "Brahma"},
    {"id": 5,  "nombre": "Mrigashirsha",     "regente": "Marte",    "deidad": "Soma"},
    {"id": 6,  "nombre": "Ardra",            "regente": "Rahu",     "deidad": "Rudra"},
    {"id": 7,  "nombre": "Punarvasu",        "regente": "Júpiter",  "deidad": "Aditi"},
    {"id": 8,  "nombre": "Pushya",           "regente": "Saturno",  "deidad": "Brihaspati"},
    {"id": 9,  "nombre": "Ashlesha",         "regente": "Mercurio", "deidad": "Sarpa"},
    {"id": 10, "nombre": "Magha",            "regente": "Ketu",     "deidad": "Pitris"},
    {"id": 11, "nombre": "Purva Phalguni",   "regente": "Venus",    "deidad": "Bhaga"},
    {"id": 12, "nombre": "Uttara Phalguni",  "regente": "Sol",      "deidad": "Aryaman"},
    {"id": 13, "nombre": "Hasta",            "regente": "Luna",     "deidad": "Savitri"},
    {"id": 14, "nombre": "Chitra",           "regente": "Marte",    "deidad": "Tvashtar"},
    {"id": 15, "nombre": "Swati",            "regente": "Rahu",     "deidad": "Vayu"},
    {"id": 16, "nombre": "Vishakha",         "regente": "Júpiter",  "deidad": "Indra-Agni"},
    {"id": 17, "nombre": "Anuradha",         "regente": "Saturno",  "deidad": "Mitra"},
    {"id": 18, "nombre": "Jyeshtha",         "regente": "Mercurio", "deidad": "Indra"},
    {"id": 19, "nombre": "Mula",             "regente": "Ketu",     "deidad": "Nirrti"},
    {"id": 20, "nombre": "Purva Ashadha",    "regente": "Venus",    "deidad": "Apah"},
    {"id": 21, "nombre": "Uttara Ashadha",   "regente": "Sol",      "deidad": "Vishvedevas"},
    {"id": 22, "nombre": "Shravana",         "regente": "Luna",     "deidad": "Vishnu"},
    {"id": 23, "nombre": "Dhanishtha",       "regente": "Marte",    "deidad": "Ashta Vasus"},
    {"id": 24, "nombre": "Shatabhisha",      "regente": "Rahu",     "deidad": "Varuna"},
    {"id": 25, "nombre": "Purva Bhadrapada", "regente": "Júpiter",  "deidad": "Aja Ekapada"},
    {"id": 26, "nombre": "Uttara Bhadrapada","regente": "Saturno",  "deidad": "Ahirbudhnya"},
    {"id": 27, "nombre": "Revati",           "regente": "Mercurio", "deidad": "Pushan"},
]

# Vimshottari: regente-nakshatra → (nombre_dasha, años)
VIMSHOTTARI = [
    ("Ketu", 7), ("Venus", 20), ("Sol", 6), ("Luna", 10), ("Marte", 7),
    ("Rahu", 18), ("Júpiter", 16), ("Saturno", 19), ("Mercurio", 17),
]
DASHA_TOTAL = 120

# Mapeado nakshatra → índice Vimshottari (0-8, repite cada 9)
NAK_TO_DASHA = [i % 9 for i in range(27)]

# Exaltación: planeta → (signo_idx, grado_exaltacion)
EXALT = {
    "Sol": (0, 10), "Luna": (1, 3), "Marte": (9, 28), "Mercurio": (5, 15),
    "Júpiter": (3, 5), "Venus": (11, 27), "Saturno": (6, 20),
}
DEBIT = {
    "Sol": (6, 10), "Luna": (7, 3), "Marte": (3, 28), "Mercurio": (11, 15),
    "Júpiter": (9, 5), "Venus": (5, 27), "Saturno": (0, 20),
}
MOOL = {
    "Sol": (4, 0, 20), "Luna": (1, 4, 20), "Marte": (0, 0, 12),
    "Mercurio": (5, 15, 20), "Júpiter": (8, 0, 10), "Venus": (6, 0, 15), "Saturno": (10, 0, 20),
}
OWN = {
    "Sol": [4], "Luna": [3], "Marte": [0, 7], "Mercurio": [2, 5],
    "Júpiter": [8, 11], "Venus": [1, 6], "Saturno": [9, 10],
}
NAISARGIKA = {"Sol": 60.0, "Luna": 51.43, "Marte": 17.14, "Mercurio": 25.71, "Júpiter": 34.29, "Venus": 42.86, "Saturno": 8.57}
DIG_BALA_HOUSE = {"Sol": 9, "Marte": 9, "Júpiter": 0, "Mercurio": 0, "Venus": 3, "Luna": 3, "Saturno": 6}

# Planetas en orden para el motor (sin Rahu/Ketu que se calculan aparte)
PLANET_NAMES = ["Sol", "Luna", "Marte", "Mercurio", "Júpiter", "Venus", "Saturno"]
GENDER = {"Sol": "M", "Marte": "M", "Júpiter": "M", "Luna": "F", "Venus": "F", "Saturno": "N", "Mercurio": "N"}

# Ashtakavarga — tabla clásica de Parashara
# Para cada planeta P: dict {ref_planeta: [casas_que_contribuyen 0-indexed]}
# Número de casas contadas desde la posición del planeta de referencia
AVG_TABLE: dict[str, dict[str, list[int]]] = {
    "Sol": {
        "Sol":      [0,1,3,6,7,8,9,10],
        "Luna":     [2,5,9,10],
        "Marte":    [0,1,3,6,7,8,9,10],
        "Mercurio": [2,4,5,8,11],
        "Júpiter":  [4,5,8,10],
        "Venus":    [5,6,11],
        "Saturno":  [0,1,3,6,7,8,9,10],
        "Lagna":    [0,1,3,6,7,8,9,10],
    },
    "Luna": {
        "Sol":      [2,5,6,7,9,10],
        "Luna":     [0,2,5,6,9,10],
        "Marte":    [1,2,4,5,8,9,10],
        "Mercurio": [0,2,3,4,6,7,9,10],
        "Júpiter":  [0,3,6,7,9,10],
        "Venus":    [2,3,4,6,8,9,10],
        "Saturno":  [2,4,5,10],
        "Lagna":    [2,5,9,10],
    },
    "Marte": {
        "Sol":      [2,4,5,9,10],
        "Luna":     [2,5,10],
        "Marte":    [0,1,3,6,7,8,9,10],
        "Mercurio": [2,4,5,10],
        "Júpiter":  [5,9,10,11],
        "Venus":    [5,7,10,11],
        "Saturno":  [0,3,6,7,8,9,10],
        "Lagna":    [0,1,3,6,7,8,9,10],
    },
    "Mercurio": {
        "Sol":      [4,5,8,9,10,11],
        "Luna":     [1,2,3,4,5,7,8,9],
        "Marte":    [0,2,3,4,6,11],
        "Mercurio": [0,2,3,4,5,8,9,11],
        "Júpiter":  [0,5,8,9,10,11],
        "Venus":    [0,1,2,3,5,6,9,11],
        "Saturno":  [0,5,7,10,11],
        "Lagna":    [0,2,3,4,5,8,9,11],
    },
    "Júpiter": {
        "Sol":      [0,1,5,8,9,10,11],
        "Luna":     [0,1,2,3,5,6,9,10],
        "Marte":    [0,1,4,5,8,10,11],
        "Mercurio": [0,1,2,3,5,8,9],
        "Júpiter":  [0,1,2,3,4,6,8,10],
        "Venus":    [0,1,2,3,8,9,11],
        "Saturno":  [0,4,5,6,8,10,11],
        "Lagna":    [0,1,5,6,8,9,10],
    },
    "Venus": {
        "Sol":      [0,7,9,10,11],
        "Luna":     [0,2,5,6,7,8,11],
        "Marte":    [0,2,3,4,7,8,11],
        "Mercurio": [0,2,3,4,5,9,10,11],
        "Júpiter":  [0,1,5,8,9,10,11],
        "Venus":    [0,1,2,3,4,5,8,9],
        "Saturno":  [0,4,5,6,7,11],
        "Lagna":    [0,1,2,3,7,8,9,10],
    },
    "Saturno": {
        "Sol":      [0,5,6,8,9,10,11],
        "Luna":     [2,4,5,6,7,8,11],
        "Marte":    [0,2,3,4,7,8,10,11],
        "Mercurio": [0,1,2,3,4,8,9,10],
        "Júpiter":  [4,5,6,9,10,11],
        "Venus":    [0,4,5,8,9,11],
        "Saturno":  [0,2,3,4,5,6,8,10],
        "Lagna":    [0,2,3,4,5,8,9,10],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 2. UTILIDADES ASTRONÓMICAS
# ─────────────────────────────────────────────────────────────────────────────

def _geocode(ciudad: str) -> dict:
    r = requests.get(
        "https://api.opencagedata.com/geocode/v1/json",
        params={"q": ciudad, "key": OPENCAGE_KEY, "limit": 1, "language": "es"},
        timeout=10,
    )
    r.raise_for_status()
    results = r.json().get("results", [])
    if not results:
        raise ValueError(f"Ciudad no encontrada: {ciudad}")
    g = results[0]["geometry"]
    return {"lat": g["lat"], "lon": g["lng"]}


def _tz_name(lat: float, lon: float) -> str:
    tz = TZF.timezone_at(lat=lat, lng=lon)
    return tz or "UTC"


def _to_utc(fecha: str, hora: str, tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    naive = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    return tz.localize(naive).astimezone(pytz.utc)


def _jd(dt_utc: datetime) -> float:
    d = ephem.Date(dt_utc.strftime("%Y/%m/%d %H:%M:%S"))
    return float(d) + 2415020.0  # Dublin JD → JD


def _lahiri(jd: float) -> float:
    """Lahiri ayanamsa para un Julian Day dado."""
    years = (jd - 2451545.0) / 365.25  # años desde J2000
    return (23.85358 + years * 0.013955) % 360


def _tropical_lon(body: ephem.Body, date_str: str) -> float:
    body.compute(date_str, epoch=date_str)
    ecl = ephem.Ecliptic(body, epoch=date_str)
    return math.degrees(float(ecl.lon)) % 360


def _sidereal_lon(body: ephem.Body, date_str: str, ayanamsa: float) -> float:
    return (_tropical_lon(body, date_str) - ayanamsa) % 360


def _mean_rahu(jd: float, ayanamsa: float) -> float:
    T = (jd - 2451545.0) / 36525.0
    rahu_trop = (125.0445479 - 1934.1362608 * T + 0.0020762 * T * T) % 360
    return (rahu_trop - ayanamsa) % 360


def _true_rahu(dt_utc: datetime, ayanamsa: float) -> float:
    """True ascending node via Moon ecliptic latitude=0 ascending crossing (±10 days, 4h steps + bisection)."""
    def _lat_lon(d: datetime) -> tuple:
        s = d.strftime("%Y/%m/%d %H:%M:%S")
        m = ephem.Moon()
        m.compute(s, epoch=s)
        ecl = ephem.Ecliptic(m, epoch=s)
        return math.degrees(float(ecl.lat)), math.degrees(float(ecl.lon)) % 360

    best_dist = float("inf")
    best_lon = None

    prev_lat, _ = _lat_lon(dt_utc - timedelta(hours=10 * 24 + 4))

    for h in range(-10 * 24, 10 * 24, 4):
        curr_dt = dt_utc + timedelta(hours=h)
        curr_lat, _ = _lat_lon(curr_dt)
        if prev_lat < 0 <= curr_lat:  # ascending zero-crossing (= Rahu)
            lo = curr_dt - timedelta(hours=4)
            hi = curr_dt
            for _ in range(22):
                mid = lo + (hi - lo) / 2
                if _lat_lon(mid)[0] < 0:
                    lo = mid
                else:
                    hi = mid
            cross_dt = lo + (hi - lo) / 2
            _, cross_lon = _lat_lon(cross_dt)
            dist = abs((cross_dt - dt_utc).total_seconds())
            if dist < best_dist:
                best_dist = dist
                best_lon = cross_lon
        prev_lat = curr_lat

    if best_lon is None:
        # Fallback to mean node if no crossing found
        jd = _jd(dt_utc)
        return _mean_rahu(jd, ayanamsa)

    return (best_lon - ayanamsa) % 360


def _ascendant_tropical(dt_utc: datetime, lat: float, lon: float) -> float:
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = ephem.Date(dt_utc.strftime("%Y/%m/%d %H:%M:%S"))
    obs.epoch = obs.date

    lst_deg = math.degrees(float(obs.sidereal_time())) % 360

    # Obliquity of ecliptic
    T = (float(obs.date) - ephem.J2000) / 36525
    eps = 23.439291111 - 0.013004167 * T
    eps_r = math.radians(eps)
    lst_r = math.radians(lst_deg)
    lat_r = math.radians(lat)

    y = math.cos(lst_r)
    x = -(math.sin(lst_r) * math.cos(eps_r) + math.tan(lat_r) * math.sin(eps_r))
    asc = math.degrees(math.atan2(y, x)) % 360
    return asc


def _mc_tropical(dt_utc: datetime, lat: float, lon: float) -> float:
    obs = ephem.Observer()
    obs.lat, obs.lon = str(lat), str(lon)
    obs.date = ephem.Date(dt_utc.strftime("%Y/%m/%d %H:%M:%S"))
    obs.epoch = obs.date
    lst_deg = math.degrees(float(obs.sidereal_time())) % 360
    T = (float(obs.date) - ephem.J2000) / 36525
    eps = 23.439291111 - 0.013004167 * T
    eps_r = math.radians(eps)
    ramc_r = math.radians(lst_deg)
    mc = math.degrees(math.atan2(math.sin(ramc_r), math.cos(ramc_r) * math.cos(eps_r))) % 360
    return mc


# ─────────────────────────────────────────────────────────────────────────────
# 3. FUNCIONES DE SIGNOS / NAKSHATRAS / GRADOS
# ─────────────────────────────────────────────────────────────────────────────

def _fmt(lon: float) -> str:
    """Formatea longitud como 'GG°MM'SS' NombreSigno'."""
    s = int(lon / 30)
    d = lon % 30
    deg = int(d)
    mn = int((d - deg) * 60)
    sec = int(((d - deg) * 60 - mn) * 60)
    return f"{deg:02d}°{mn:02d}'{sec:02d}\" {SIGNOS[s]['nombre']}"


def _sign(lon: float) -> int:
    return int(lon / 30) % 12


def _deg_in_sign(lon: float) -> float:
    return lon % 30


def _nakshatra_info(lon: float) -> dict:
    nak_size = 360 / 27  # 13.333...°
    pada_size = nak_size / 4
    idx = int(lon / nak_size) % 27  # 0-based
    pos_in_nak = lon % nak_size
    pada = int(pos_in_nak / pada_size) + 1
    n = NAKSHATRAS[idx]
    return {"nombre": n["nombre"], "pada": pada, "regente": n["regente"], "deidad": n["deidad"]}


def _dignity(planet: str, sign_idx: int) -> str:
    if sign_idx in OWN.get(planet, []):
        return "Propio"
    if EXALT.get(planet, (None,))[0] == sign_idx:
        return "Exaltado"
    if DEBIT.get(planet, (None,))[0] == sign_idx:
        return "Débil"
    m = MOOL.get(planet)
    if m and m[0] == sign_idx:
        return "Moolatrikona"
    return "—"


# ─────────────────────────────────────────────────────────────────────────────
# 4. POSICIONES DE PLANETAS
# ─────────────────────────────────────────────────────────────────────────────

def _all_planets(dt_utc: datetime, ayanamsa: float, lat: float, lon: float) -> dict:
    date_str = dt_utc.strftime("%Y/%m/%d %H:%M:%S")

    bodies = {
        "Sol":      ephem.Sun(),
        "Luna":     ephem.Moon(),
        "Marte":    ephem.Mars(),
        "Mercurio": ephem.Mercury(),
        "Júpiter":  ephem.Jupiter(),
        "Venus":    ephem.Venus(),
        "Saturno":  ephem.Saturn(),
    }

    planets = {}
    for name, body in bodies.items():
        body.compute(date_str, epoch=date_str)
        trop = math.degrees(float(ephem.Ecliptic(body, epoch=date_str).lon)) % 360
        sid = (trop - ayanamsa) % 360
        s = _sign(sid)
        d = _deg_in_sign(sid)
        # Speed (degrees/day) for retrograde detection
        body2 = bodies[name].__class__()
        body2.compute(ephem.Date(float(ephem.Date(date_str)) + 1), epoch=date_str)
        trop2 = math.degrees(float(ephem.Ecliptic(body2, epoch=date_str).lon)) % 360
        speed = ((trop2 - trop + 540) % 360) - 180
        planets[name] = {
            "lon": round(sid, 6),
            "signo": SIGNOS[s]["nombre"],
            "signo_idx": s,
            "grado": _fmt(sid),
            "deg_en_signo": round(d, 4),
            "retrograde": speed < 0,
            "speed_dia": round(speed, 4),
            "dignidad": _dignity(name, s),
            "nakshatra": _nakshatra_info(sid),
        }

    # Rahu y Ketu (Nodo Verdadero — cruce ascendente latitud eclíptica lunar)
    rahu_sid = _true_rahu(dt_utc, ayanamsa)
    ketu_sid = (rahu_sid + 180) % 360
    for name, sid in [("Rahu", rahu_sid), ("Ketu", ketu_sid)]:
        s = _sign(sid)
        planets[name] = {
            "lon": round(sid, 6),
            "signo": SIGNOS[s]["nombre"],
            "signo_idx": s,
            "grado": _fmt(sid),
            "deg_en_signo": round(_deg_in_sign(sid), 4),
            "retrograde": False,   # Rahu/Ketu son siempre retrógrados por naturaleza pero no se marcan así
            "speed_dia": -0.053,
            "dignidad": "—",
            "nakshatra": _nakshatra_info(sid),
        }

    # Ascendente (Lagna)
    asc_trop = _ascendant_tropical(dt_utc, lat, lon)
    asc_sid = (asc_trop - ayanamsa) % 360
    s = _sign(asc_sid)
    planets["Lagna"] = {
        "lon": round(asc_sid, 6),
        "signo": SIGNOS[s]["nombre"],
        "signo_idx": s,
        "grado": _fmt(asc_sid),
        "deg_en_signo": round(_deg_in_sign(asc_sid), 4),
        "retrograde": False,
        "speed_dia": None,
        "dignidad": "—",
        "nakshatra": _nakshatra_info(asc_sid),
    }

    return planets


def _casa_whole_sign(planet_sign: int, lagna_sign: int) -> int:
    """Número de casa en sistema Whole Sign (1-12)."""
    return (planet_sign - lagna_sign) % 12 + 1


# ─────────────────────────────────────────────────────────────────────────────
# 5. D1 CARTA NATAL
# ─────────────────────────────────────────────────────────────────────────────

def _d1(planets: dict) -> dict:
    lagna_sign = planets["Lagna"]["signo_idx"]
    out = []
    for name, p in planets.items():
        entry = {
            "planeta": name,
            "signo": p["signo"],
            "signo_idx": p["signo_idx"],
            "grado": p["grado"],
            "deg_en_signo": round(p["deg_en_signo"], 2),
            "casa": _casa_whole_sign(p["signo_idx"], lagna_sign),
            "retrograde": p["retrograde"],
            "dignidad": p["dignidad"],
            "nakshatra": p["nakshatra"]["nombre"],
            "pada": p["nakshatra"]["pada"],
        }
        out.append(entry)
    lp = planets["Lagna"]
    return {
        "lagna": {
            "signo": lp["signo"],
            "signo_idx": lp["signo_idx"],
            "grado": lp["grado"],
            "deg_en_signo": round(lp["deg_en_signo"], 2),
        },
        "planetas": out,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. CARTAS VARGA (D9, D10)
# ─────────────────────────────────────────────────────────────────────────────

def _varga_lon(lon: float, division: int) -> float:
    """
    Calcula la longitud sidereal en la carta Varga de orden `division`.
    D9: division=9, D10: division=10, etc.
    """
    sign_idx = int(lon / 30)
    pos_in_sign = lon % 30
    part_size = 30.0 / division
    part_num = int(pos_in_sign / part_size)  # 0 to division-1

    # Sign offset según modalidad (Móvil/Fijo/Dual) para D9 Navamsha
    if division == 9:
        modal = sign_idx % 3
        if modal == 0:   start = 0   # Móvil → Aries
        elif modal == 1: start = 9   # Fijo → Capricornio
        else:            start = 6   # Dual → Libra
    elif division == 10:
        if sign_idx % 2 == 0: start = sign_idx       # signo impar → propio
        else: start = (sign_idx + 9) % 12             # signo par → décima desde el signo
    else:
        start = 0  # fallback

    result_sign = (start + part_num) % 12
    return result_sign * 30 + pos_in_sign % part_size * (30.0 / part_size)


def _varga_chart(planets: dict, division: int) -> dict:
    lagna_lon = _varga_lon(planets["Lagna"]["lon"], division)
    lagna_sign = _sign(lagna_lon)
    out = []
    for name, p in planets.items():
        if name == "Lagna":
            continue
        vlon = _varga_lon(p["lon"], division)
        vs = _sign(vlon)
        out.append({
            "planeta": name,
            "signo": SIGNOS[vs]["nombre"],
            "grado": _fmt(vlon),
            "casa": _casa_whole_sign(vs, lagna_sign),
            "dignidad": _dignity(name, vs) if name in PLANET_NAMES else "—",
        })
    return {
        "lagna": {"signo": SIGNOS[lagna_sign]["nombre"], "grado": _fmt(lagna_lon)},
        "planetas": out,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. VIMSHOTTARI DASHA (3 niveles con fechas exactas)
# ─────────────────────────────────────────────────────────────────────────────

def _dasha_balance(moon_lon: float) -> tuple[str, float]:
    """Retorna (planeta_dasha_nacimiento, años_restantes)."""
    nak_size = 360 / 27
    nak_idx = int(moon_lon / nak_size) % 27
    dasha_idx = NAK_TO_DASHA[nak_idx]
    dasha_name, dasha_years = VIMSHOTTARI[dasha_idx]
    pos_in_nak = moon_lon % nak_size
    fraction_elapsed = pos_in_nak / nak_size
    elapsed_years = fraction_elapsed * dasha_years
    remaining = dasha_years - elapsed_years
    return dasha_name, remaining


def _add_years(dt: datetime, years: float) -> datetime:
    days = years * 365.25
    return dt + timedelta(days=days)


def _vimshottari(moon_lon: float, birth_dt: datetime) -> dict:
    """Genera 3 niveles de dashas con fechas. Retorna ~5 Mahadashas relevantes."""
    start_planet, balance = _dasha_balance(moon_lon)

    # Índice del dasha de inicio
    start_idx = next(i for i, (n, _) in enumerate(VIMSHOTTARI) if n == start_planet)

    # Calcular secuencia de Mahadashas desde el nacimiento
    maha_list = []
    current_dt = birth_dt
    # Primer Mahadasha incompleto
    for i in range(9):
        idx = (start_idx + i) % 9
        planet, years = VIMSHOTTARI[idx]
        if i == 0:
            duration = balance
            maha_start = birth_dt
        else:
            duration = years
            maha_start = current_dt
        maha_end = _add_years(maha_start, duration)

        # Antardashas
        antardasha_list = []
        antar_start = maha_start
        for j in range(9):
            aidx = (idx + j) % 9
            ap, ay = VIMSHOTTARI[aidx]
            antar_duration = (duration * ay) / DASHA_TOTAL
            antar_end = _add_years(antar_start, antar_duration)

            # Pratyantar (solo para el antardasha vigente o el siguiente)
            pratyantar_list = []
            prat_start = antar_start
            for k in range(9):
                pidx = (aidx + k) % 9
                pp, py = VIMSHOTTARI[pidx]
                prat_duration = (antar_duration * py) / DASHA_TOTAL
                prat_end = _add_years(prat_start, prat_duration)
                pratyantar_list.append({
                    "planeta": pp,
                    "inicio": prat_start.strftime("%Y-%m-%d"),
                    "fin": prat_end.strftime("%Y-%m-%d"),
                })
                prat_start = prat_end

            antardasha_list.append({
                "planeta": ap,
                "inicio": antar_start.strftime("%Y-%m-%d"),
                "fin": antar_end.strftime("%Y-%m-%d"),
                "pratyantar": pratyantar_list,
            })
            antar_start = antar_end

        maha_list.append({
            "planeta": planet,
            "inicio": maha_start.strftime("%Y-%m-%d"),
            "fin": maha_end.strftime("%Y-%m-%d"),
            "antardashas": antardasha_list,
        })
        current_dt = maha_end

    balance_planet, balance_years = start_planet, balance
    return {
        "dasha_nacimiento": {"planeta": balance_planet, "años_restantes": round(balance, 4)},
        "mahadashas": maha_list,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 8. SADE SATI (3 fases con fechas exactas)
# ─────────────────────────────────────────────────────────────────────────────

def _saturn_sid_on(jd_target: float, ayanamsa_ref: float) -> float:
    dt = datetime(1858, 11, 17) + timedelta(days=jd_target - 2400000.5)
    date_str = dt.strftime("%Y/%m/%d %H:%M:%S")
    sat = ephem.Saturn()
    sat.compute(date_str, epoch=date_str)
    trop = math.degrees(float(ephem.Ecliptic(sat, epoch=date_str).lon)) % 360
    jd_exact = float(ephem.Date(date_str)) + 2415020.0
    ayan = _lahiri(jd_exact)
    return (trop - ayan) % 360


def _find_saturn_sign_crossing(target_sign: int, jd_start: float, direction: int = 1) -> Optional[float]:
    """Encuentra el JD en que Saturno entra a target_sign buscando desde jd_start."""
    step = 20 * direction
    jd = jd_start
    ayan = _lahiri(jd_start)
    prev_sign = _sign(_saturn_sid_on(jd, ayan))

    for _ in range(500):
        jd += step
        ayan = _lahiri(jd)
        curr_sign = _sign(_saturn_sid_on(jd, ayan))
        if curr_sign == target_sign and prev_sign != target_sign:
            # Bisección para refinar
            lo, hi = jd - abs(step), jd
            if direction < 0:
                lo, hi = jd, jd + abs(step)
            for _ in range(30):
                mid = (lo + hi) / 2
                ayan_m = _lahiri(mid)
                mid_sign = _sign(_saturn_sid_on(mid, ayan_m))
                if mid_sign == target_sign:
                    hi = mid
                else:
                    lo = mid
            return (lo + hi) / 2
        prev_sign = curr_sign
    return None


def _jd_to_date(jd: float) -> str:
    dt = ephem.Date(jd - 2415020.0)
    return ephem.Date(dt).datetime().strftime("%Y-%m-%d")


def _sade_sati(moon_sign: int, birth_jd: float) -> dict:
    """Calcula 3 ciclos de Sade Sati. Activo = basado en fecha HOY."""
    s1 = (moon_sign - 1) % 12
    s2 = moon_sign
    s3 = (moon_sign + 1) % 12

    today_jd = _jd(datetime.utcnow().replace(tzinfo=None))
    # Convertir a ephem JD format
    today_jd_real = float(ephem.Date(datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S"))) + 2415020.0

    cycles = []

    # 3 ciclos: uno pasado, uno alrededor del nacimiento, uno futuro
    for cycle_offset in [-1, 0, 1]:
        jd_search = birth_jd + cycle_offset * 29.5 * 365.25

        entry_s1 = _find_saturn_sign_crossing(s1, jd_search - 4 * 365.25, 1)
        if entry_s1 is None:
            continue
        entry_s2 = _find_saturn_sign_crossing(s2, entry_s1, 1)
        entry_s3 = _find_saturn_sign_crossing(s3, entry_s2 or entry_s1, 1)
        exit_s3 = _find_saturn_sign_crossing((s3 + 1) % 12, entry_s3 or entry_s1, 1)

        if not (entry_s1 and entry_s2 and entry_s3 and exit_s3):
            continue

        # Activo = comprobado contra HOY
        is_active = entry_s1 <= today_jd_real <= exit_s3
        fase_actual = None
        if is_active:
            if today_jd_real < entry_s2:
                fase_actual = "ascendente"
            elif today_jd_real < entry_s3:
                fase_actual = "pico"
            else:
                fase_actual = "descendente"

        cycles.append({
            "inicio": _jd_to_date(entry_s1),
            "fin": _jd_to_date(exit_s3),
            "fases": [
                {"fase": "ascendente",  "signo_saturno": SIGNOS[s1]["nombre"],
                 "inicio": _jd_to_date(entry_s1), "fin": _jd_to_date(entry_s2)},
                {"fase": "pico",        "signo_saturno": SIGNOS[s2]["nombre"],
                 "inicio": _jd_to_date(entry_s2), "fin": _jd_to_date(entry_s3)},
                {"fase": "descendente", "signo_saturno": SIGNOS[s3]["nombre"],
                 "inicio": _jd_to_date(entry_s3), "fin": _jd_to_date(exit_s3)},
            ],
            "activo": is_active,
            "fase_actual": fase_actual,
        })

    seen: set[str] = set()
    unique = []
    for c in sorted(cycles, key=lambda x: x["inicio"]):
        if c["inicio"] not in seen:
            seen.add(c["inicio"])
            unique.append(c)

    activo_ahora = next((c for c in unique if c["activo"]), None)
    return {
        "signo_lunar": SIGNOS[moon_sign]["nombre"],
        "activo_hoy": activo_ahora is not None,
        "fase_actual": activo_ahora["fase_actual"] if activo_ahora else None,
        "ciclos": unique[:3],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 9. SHAD BALA
# ─────────────────────────────────────────────────────────────────────────────

def _uccha_bala(planet: str, lon: float) -> float:
    """Exaltation strength 0–60 Shashtiamsas."""
    if planet not in EXALT:
        return 0.0
    exalt_sign, exalt_deg = EXALT[planet]
    debit_sign, debit_deg = DEBIT[planet]
    exalt_lon = exalt_sign * 30 + exalt_deg
    debit_lon = debit_sign * 30 + debit_deg
    diff = abs(lon - exalt_lon)
    if diff > 180:
        diff = 360 - diff
    return round(max(0, 60 * (1 - diff / 180)), 2)


def _saptavargaja(planet: str, sign_d1: int, sign_d9: int, sign_d10: int) -> float:
    """Dignidad en D1, D9, D10 — valor 0–135 (simplificado desde 7 vargas)."""
    total = 0.0
    weights = [3.0, 2.5, 2.0]  # D1 pesa más
    for sign, w in zip([sign_d1, sign_d9, sign_d10], weights):
        dig = _dignity(planet, sign)
        pts = {"Moolatrikona": 4.5, "Propio": 3.0, "Exaltado": 3.0, "—": 1.0, "Débil": 0.5}.get(dig, 1.0)
        total += pts * w
    return round(total, 2)


def _kendradi_bala(casa: int) -> float:
    if casa in [1, 4, 7, 10]: return 60.0
    if casa in [2, 5, 8, 11]: return 30.0
    return 15.0


def _dig_bala(planet: str, planet_lon: float, asc_lon: float, mc_lon: float) -> float:
    ic_lon = (mc_lon + 180) % 360
    dsc_lon = (asc_lon + 180) % 360
    ref = {"Sol": mc_lon, "Marte": mc_lon, "Luna": ic_lon, "Venus": ic_lon,
           "Júpiter": asc_lon, "Mercurio": asc_lon, "Saturno": dsc_lon}
    if planet not in ref:
        return 0.0
    pref = ref[planet]
    diff = abs(planet_lon - pref)
    if diff > 180:
        diff = 360 - diff
    return round(max(0, 60 * (1 - diff / 180)), 2)


def _chesta_bala(speed: float, planet: str) -> float:
    """Motional strength based on relative speed."""
    mean_speeds = {"Sol": 0.985, "Luna": 13.18, "Marte": 0.524, "Mercurio": 1.383,
                   "Júpiter": 0.083, "Venus": 1.2, "Saturno": 0.033}
    ms = mean_speeds.get(planet, 1.0)
    if speed < 0:  # retrograde
        return round(max(0, 30 * (-speed / ms)), 2)
    return round(min(60, 60 * speed / ms), 2)


def _ishta_kashta(uccha: float, chesta: float) -> tuple[float, float]:
    ishta = round(math.sqrt(uccha * chesta), 2)
    kashta = round(math.sqrt((60 - uccha) * max(0, 60 - chesta)), 2)
    return ishta, kashta


def _shad_bala(planets: dict, lagna_sign: int) -> list[dict]:
    asc_lon = planets["Lagna"]["lon"]
    mc_lon = (asc_lon + 90) % 360  # Aproximación — MC correcto requiere pyswisseph

    result = []
    for name in PLANET_NAMES:
        p = planets[name]
        lon = p["lon"]
        sign = p["signo_idx"]
        casa = _casa_whole_sign(sign, lagna_sign)
        speed = p["speed_dia"]

        d9_lon = _varga_lon(lon, 9)
        d10_lon = _varga_lon(lon, 10)

        uccha = _uccha_bala(name, lon)
        saptav = _saptavargaja(name, sign, _sign(d9_lon), _sign(d10_lon))
        kendra = _kendradi_bala(casa)
        dig = _dig_bala(name, lon, asc_lon, mc_lon)
        chesta = _chesta_bala(speed or 0, name)
        nais = NAISARGIKA[name]
        total = round(uccha + saptav + kendra + dig + chesta + nais, 2)
        rupas = round(total / 60, 3)
        ishta, kashta = _ishta_kashta(uccha, chesta)

        result.append({
            "planeta": name,
            "uccha_bala": uccha,
            "saptavargaja": saptav,
            "kendradi": kendra,
            "dig_bala": dig,
            "chesta_bala": chesta,
            "naisargika": nais,
            "total_shashtiamsas": total,
            "rupas": rupas,
            "ishta_phala": ishta,
            "kashta_phala": kashta,
        })

    SHADBALA_MIN_RUPAS = {
        "Sol": 6.5, "Luna": 6.0, "Marte": 5.0,
        "Mercurio": 7.0, "Júpiter": 6.5, "Venus": 5.5, "Saturno": 5.0,
    }
    ranked = sorted(range(len(result)), key=lambda i: result[i]["total_shashtiamsas"], reverse=True)
    rank_map = {result[i]["planeta"]: r + 1 for r, i in enumerate(ranked)}
    for item in result:
        min_r = SHADBALA_MIN_RUPAS.get(item["planeta"], 5.0)
        item["minimo_rupas"] = min_r
        item["pct_minimo"] = round((item["rupas"] / min_r) * 100, 1)
        item["rango"] = rank_map[item["planeta"]]
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 10. ASHTAKAVARGA
# ─────────────────────────────────────────────────────────────────────────────

def _bav_planet(planet: str, planets: dict) -> list[int]:
    """Bhinnashtakavarga para un planeta: lista de 12 bindus (por signo 0-11)."""
    bindus = [0] * 12
    p_sign = planets[planet]["signo_idx"]
    lagna_sign = planets["Lagna"]["signo_idx"]

    ref_map = {
        "Sol": planets["Sol"]["signo_idx"],
        "Luna": planets["Luna"]["signo_idx"],
        "Marte": planets["Marte"]["signo_idx"],
        "Mercurio": planets["Mercurio"]["signo_idx"],
        "Júpiter": planets["Júpiter"]["signo_idx"],
        "Venus": planets["Venus"]["signo_idx"],
        "Saturno": planets["Saturno"]["signo_idx"],
        "Lagna": lagna_sign,
    }

    table = AVG_TABLE.get(planet, {})
    for ref_name, ref_sign in ref_map.items():
        offsets = table.get(ref_name, [])
        for offset in offsets:
            target_sign = (ref_sign + offset) % 12
            bindus[target_sign] += 1
    return bindus


def _ashtakavarga(planets: dict) -> dict:
    bav = {}
    samudaya = [0] * 12
    for planet in PLANET_NAMES:
        b = _bav_planet(planet, planets)
        bav[planet] = b
        for i in range(12):
            samudaya[i] += b[i]
    return {
        "samudaya": samudaya,
        "bhinnashtaka": {
            p: {SIGNOS[i]["nombre"]: bav[p][i] for i in range(12)} for p in PLANET_NAMES
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 11. JAIMINI CHARA KARAKAS (7 planetas — sin nodos)
# ─────────────────────────────────────────────────────────────────────────────

def _jaimini_karakas(planets: dict) -> tuple[dict, list]:
    """7 Karakas según Jaimini (excluye Rahu/Ketu).
    Retorna (simple_dict, detalle_list) para compatibilidad con prompts y UI."""
    ordered = sorted(PLANET_NAMES, key=lambda n: planets[n]["deg_en_signo"], reverse=True)
    karaka_defs = [
        ("Atmakaraka (AK)",    "AK"),
        ("Amatyakaraka (AMK)", "AMK"),
        ("Bhratrikaraka (BK)", "BK"),
        ("Matrikaraka (MK)",   "MK"),
        ("Putrakaraka (PK)",   "PK"),
        ("Gnatikaraka (GK)",   "GK"),
        ("Darakaraka (DK)",    "DK"),
    ]
    simple:  dict = {}
    detalle: list = []
    for i, (karaka, abr) in enumerate(karaka_defs):
        if i < len(ordered):
            p = ordered[i]
            simple[karaka] = p
            detalle.append({
                "karaka": karaka,
                "abr": abr,
                "planeta": p,
                "signo": planets[p]["signo"],
                "deg_en_signo": round(planets[p]["deg_en_signo"], 2),
            })
    return simple, detalle


# ─────────────────────────────────────────────────────────────────────────────
# 11b. KARAKAMSHA · UPAPADA LAGNA
# ─────────────────────────────────────────────────────────────────────────────

def _karakamsha(planets: dict, karakas: dict) -> dict:
    """Karakamsha = navamsha sign of the Atmakaraka planet."""
    ak = karakas.get("Atmakaraka (AK)")
    if not ak or ak not in planets:
        return {"planeta_ak": str(ak), "signo": "—", "signo_idx": -1}
    d9_lon = _varga_lon(planets[ak]["lon"], 9)
    sign = _sign(d9_lon)
    return {"planeta_ak": ak, "signo": SIGNOS[sign]["nombre"], "signo_idx": sign}


def _arudha_pada_sign(house_num: int, lagna_sign: int, planets: dict) -> int:
    """Arudha Pada sign for a given house number (1-12, Whole Sign, Parashara rules)."""
    house_sign = (lagna_sign + house_num - 1) % 12
    lord = SIGNOS[house_sign]["reg"]
    lord_sign = planets[lord]["signo_idx"]
    n = (lord_sign - house_sign) % 12 + 1
    arudha = (lord_sign + n - 1) % 12
    if arudha == house_sign:
        arudha = (house_sign + 9) % 12      # 10th from bhava
    elif arudha == (house_sign + 6) % 12:
        arudha = (house_sign + 3) % 12      # 4th from bhava
    return arudha


def _upapada_lagna(lagna_sign: int, planets: dict) -> dict:
    """Upapada Lagna = Arudha Pada of the 12th house (Jaimini)."""
    sign_idx = _arudha_pada_sign(12, lagna_sign, planets)
    h12_lord = SIGNOS[(lagna_sign + 11) % 12]["reg"]
    return {
        "signo": SIGNOS[sign_idx]["nombre"],
        "signo_idx": sign_idx,
        "lord_casa12": h12_lord,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 12. DOSHAS AYURVÉDICOS (algoritmo Tattva)
# ─────────────────────────────────────────────────────────────────────────────

def _doshas_ayurvedicos(planets: dict) -> dict:
    """
    Pitta = Fuego (Sol, Marte) · Vata = Aire + Éter (Mercurio, Saturno, Rahu)
    Kapha = Agua + Tierra (Luna, Venus, Júpiter)
    Pesos: Lagna x3, Luna x2, Sol x2, resto x1
    """
    tattva = {
        "Sol": "Pitta", "Luna": "Kapha", "Marte": "Pitta",
        "Mercurio": "Vata", "Júpiter": "Kapha", "Venus": "Kapha", "Saturno": "Vata",
        "Rahu": "Vata", "Ketu": "Pitta",
    }
    elem_dosha = {"Fuego": "Pitta", "Tierra": "Kapha", "Agua": "Kapha", "Aire": "Vata"}
    weights = {"Sol": 2, "Luna": 2, "Lagna": 3}
    scores = {"Vata": 0, "Pitta": 0, "Kapha": 0}

    for name, p in planets.items():
        if name == "Lagna":
            sign_elem = SIGNOS[p["signo_idx"]]["elem"]
            dosha = elem_dosha.get(sign_elem, "Vata")
        else:
            dosha = tattva.get(name, "Vata")
        w = weights.get(name, 1)
        scores[dosha] += w

    total = sum(scores.values())
    pct = {k: round(v * 100 / total) for k, v in scores.items()}
    predominante = max(scores, key=scores.get)
    return {
        "predominante": predominante,
        "breakdown_pct": pct,
        "descripcion": f"Constitución {predominante} predominante — {pct[predominante]}%",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 13. MOON CHART (CHANDRA LAGNA)
# ─────────────────────────────────────────────────────────────────────────────

def _moon_chart(planets: dict) -> dict:
    moon_sign = planets["Luna"]["signo_idx"]
    out = []
    for name, p in planets.items():
        if name == "Lagna":
            continue
        casa = _casa_whole_sign(p["signo_idx"], moon_sign)
        out.append({
            "planeta": name,
            "signo": p["signo"],
            "grado": p["grado"],
            "casa": casa,
        })
    return {
        "lagna": {"signo": SIGNOS[moon_sign]["nombre"], "nota": "Chandra Lagna"},
        "planetas": out,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 14. BHAVA SPASHTA (Porphyry / aproximación Sripati)
# ─────────────────────────────────────────────────────────────────────────────

def _bhava_sripati(asc_lon: float, mc_lon: float) -> list[dict]:
    """
    Bhava Spashta usando el sistema Porphyry (aproximación Sripati).
    Para Sripati exacto se necesita pyswisseph: pip install pyswisseph
    (requiere Microsoft C++ Build Tools en Windows).
    """
    ic_lon = (mc_lon + 180) % 360
    dsc_lon = (asc_lon + 180) % 360

    def arc_between(a: float, b: float) -> float:
        diff = (b - a) % 360
        return diff

    # Arco ASC → MC (yendo hacia adelante en zodíaco)
    arc_asc_mc = arc_between(asc_lon, mc_lon)
    # Arco ASC → DSC
    arc_asc_dsc = 180.0

    step_upper = arc_asc_mc / 3  # Casas 12, 11, 10
    step_lower = arc_asc_dsc / 3  # Casas 2, 3

    cusps = [None] * 12
    cusps[0]  = asc_lon                          # Casa 1 = Lagna
    cusps[9]  = mc_lon                            # Casa 10 = MC
    cusps[3]  = ic_lon                            # Casa 4 = IC
    cusps[6]  = dsc_lon                           # Casa 7 = DSC
    cusps[11] = (asc_lon - step_upper) % 360     # Casa 12
    cusps[10] = (asc_lon - 2 * step_upper) % 360 # Casa 11
    cusps[1]  = (asc_lon + arc_asc_dsc / 3) % 360  # Casa 2
    cusps[2]  = (asc_lon + 2 * arc_asc_dsc / 3) % 360  # Casa 3
    # Casas opuestas
    for i in range(4, 7):
        cusps[i] = (cusps[i - 6] + 180) % 360 if cusps[i - 6] is not None else None
    cusps[4]  = (cusps[10] + 180) % 360
    cusps[5]  = (cusps[11] + 180) % 360
    cusps[7]  = (cusps[1]  + 180) % 360
    cusps[8]  = (cusps[2]  + 180) % 360

    result = []
    for i in range(12):
        if cusps[i] is None:
            continue
        c_lon = cusps[i]
        sign = _sign(c_lon)
        lord = SIGNOS[sign]["reg"]
        next_lon = cusps[(i + 1) % 12]
        diff = (next_lon - c_lon + 360) % 360
        sandhi_lon = (c_lon + diff / 2) % 360
        result.append({
            "casa": i + 1,
            "cusp": _fmt(c_lon),
            "cusp_lon": round(c_lon, 4),
            "signo": SIGNOS[sign]["nombre"],
            "lord": lord,
            "sandhi": _fmt(sandhi_lon),
        })
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 15. YOGAS Y MANGAL DOSHA
# ─────────────────────────────────────────────────────────────────────────────

def _yogas(planets: dict) -> list[dict]:
    lagna_sign = planets["Lagna"]["signo_idx"]
    found = []

    def sign_of(p): return planets[p]["signo_idx"]
    def casa(p): return _casa_whole_sign(sign_of(p), lagna_sign)

    # ── Mahapurusha Yogas ──────────────────────────────────────────────────
    pancha = {
        "Ruchaka": ("Marte",    [0,6,9]),   # Marte en kendra en domicilio/exalt
        "Bhadra":  ("Mercurio", [2,5]),
        "Hamsa":   ("Júpiter",  [3,8,11]),  # Júpiter en kendra propio/exalt
        "Malavya": ("Venus",    [1,6]),
        "Shasha":  ("Saturno",  [9,10]),
    }
    kendra_casas = {1, 4, 7, 10}
    for yoga, (p, signs) in pancha.items():
        if sign_of(p) in signs and casa(p) in kendra_casas:
            found.append({"nombre": yoga, "tipo": "Mahapurusha",
                         "planetas": [p],
                         "descripcion": f"{p} en kendra en {planets[p]['signo']}"})

    # ── Dhana Yogas (riqueza) ──────────────────────────────────────────────
    # Señores de casas 1,2,5,9,11 mutuamente relacionados
    lords = {s: SIGNOS[s]["reg"] for s in range(12)}
    l1 = lords[lagna_sign]
    l2 = lords[(lagna_sign + 1) % 12]
    l9 = lords[(lagna_sign + 8) % 12]
    l11 = lords[(lagna_sign + 10) % 12]

    if sign_of(l1) == sign_of(l2) or sign_of(l1) == sign_of(l9):
        found.append({"nombre": "Dhana Yoga",  "tipo": "Dhana",
                      "planetas": [l1, l2 if sign_of(l1)==sign_of(l2) else l9],
                      "descripcion": "Señores de casas de riqueza conjuntos"})

    # ── Raja Yogas (poder/éxito) ──────────────────────────────────────────
    # Señores de kendra y trikona en conjunción o mutua aspecto
    kendra_lords = {lords[(lagna_sign + k) % 12] for k in [0, 3, 6, 9]}
    trikona_lords = {lords[(lagna_sign + t) % 12] for t in [0, 4, 8]}
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl != tl and sign_of(kl) == sign_of(tl):
                found.append({"nombre": "Raja Yoga", "tipo": "Raja",
                               "planetas": [kl, tl],
                               "descripcion": f"Señores de kendra ({kl}) y trikona ({tl}) conjuntos en {planets[kl]['signo']}"})

    # ── Gajakesari Yoga ────────────────────────────────────────────────────
    moon_casa = casa("Luna")
    jup_casa = casa("Júpiter")
    if abs(moon_casa - jup_casa) in [0, 3, 6, 9]:
        found.append({"nombre": "Gajakesari Yoga", "tipo": "Especial",
                      "planetas": ["Júpiter", "Luna"],
                      "descripcion": "Júpiter en kendra desde la Luna"})

    # ── Budha-Aditya Yoga ─────────────────────────────────────────────────
    if sign_of("Sol") == sign_of("Mercurio"):
        found.append({"nombre": "Budha-Aditya Yoga", "tipo": "Especial",
                      "planetas": ["Sol", "Mercurio"],
                      "descripcion": "Sol y Mercurio en el mismo signo"})

    # ── Chandra-Mangal Yoga ────────────────────────────────────────────────
    if sign_of("Luna") == sign_of("Marte"):
        found.append({"nombre": "Chandra-Mangal Yoga", "tipo": "Especial",
                      "planetas": ["Luna", "Marte"],
                      "descripcion": "Luna y Marte conjuntos"})

    return found


def _mangal_dosha(planets: dict) -> dict:
    lagna_sign = planets["Lagna"]["signo_idx"]
    moon_sign = planets["Luna"]["signo_idx"]
    venus_sign = planets["Venus"]["signo_idx"]
    mars_casa_lagna = _casa_whole_sign(planets["Marte"]["signo_idx"], lagna_sign)
    mars_casa_moon = _casa_whole_sign(planets["Marte"]["signo_idx"], moon_sign)
    mars_casa_venus = _casa_whole_sign(planets["Marte"]["signo_idx"], venus_sign)

    dosha_casas = {1, 4, 7, 8, 12}
    presente_lagna = mars_casa_lagna in dosha_casas
    presente_moon = mars_casa_moon in dosha_casas

    presente = presente_lagna or presente_moon
    intensidad = "Alta" if mars_casa_lagna in {7, 8} else ("Media" if presente else "Ninguna")

    # Cancelaciones clásicas
    cancelaciones = []
    if planets["Marte"]["signo_idx"] in OWN.get("Marte", []):
        cancelaciones.append("Marte en domicilio propio")
    if EXALT.get("Marte", (None,))[0] == planets["Marte"]["signo_idx"]:
        cancelaciones.append("Marte exaltado (Capricornio)")

    return {
        "presente": presente,
        "intensidad": intensidad,
        "casa_desde_lagna": mars_casa_lagna,
        "casa_desde_luna": mars_casa_moon,
        "cancelaciones": cancelaciones,
        "descripcion": f"Marte en Casa {mars_casa_lagna} (Lagna) · Casa {mars_casa_moon} (Luna)",
    }


# ─────────────────────────────────────────────────────────────────────────────
# 16. FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def get_birth_data(nombre: str, fecha: str, hora: str, ciudad: str) -> dict:
    """
    Motor de cálculo védico completo.

    Args:
        nombre: Nombre del consultante
        fecha:  YYYY-MM-DD
        hora:   HH:MM (24h)
        ciudad: "Bogotá, Colombia"

    Returns:
        JSON limpio listo para inyectar en Claude API
    """
    # ── Geocodificación y tiempo ──────────────────────────────────────────
    geo = _geocode(ciudad)
    lat, lon = geo["lat"], geo["lon"]
    tz_name = _tz_name(lat, lon)
    dt_utc = _to_utc(fecha, hora, tz_name)
    jd = _jd(dt_utc)
    ayanamsa = _lahiri(jd)

    # ── Posiciones planetarias ────────────────────────────────────────────
    planets = _all_planets(dt_utc, ayanamsa, lat, lon)
    lagna_sign = planets["Lagna"]["signo_idx"]
    moon_sign = planets["Luna"]["signo_idx"]

    # ── D1 Carta Natal ────────────────────────────────────────────────────
    d1 = _d1(planets)

    # ── D9 Navamsha, D10 Dashamsha ────────────────────────────────────────
    d9 = _varga_chart(planets, 9)
    d10 = _varga_chart(planets, 10)

    # ── Nakshatra de la Luna (detalle) ────────────────────────────────────
    moon_nak = _nakshatra_info(planets["Luna"]["lon"])

    # ── Vimshottari Dasha ─────────────────────────────────────────────────
    dasha = _vimshottari(planets["Luna"]["lon"], dt_utc)

    # ── Sade Sati ─────────────────────────────────────────────────────────
    sade_sati = _sade_sati(moon_sign, jd)

    # ── Shad Bala ─────────────────────────────────────────────────────────
    shad_bala = _shad_bala(planets, lagna_sign)

    # ── Ashtakavarga ──────────────────────────────────────────────────────
    ashtak = _ashtakavarga(planets)

    # ── Jaimini Karakas ───────────────────────────────────────────────────
    karakas, karakas_detalle = _jaimini_karakas(planets)
    karakamsha = _karakamsha(planets, karakas)
    upapada = _upapada_lagna(lagna_sign, planets)

    # ── Doshas Ayurvédicos ────────────────────────────────────────────────
    doshas = _doshas_ayurvedicos(planets)

    # ── Moon Chart ────────────────────────────────────────────────────────
    moon_chart = _moon_chart(planets)

    # ── Bhava Sripati ─────────────────────────────────────────────────────
    asc_lon = planets["Lagna"]["lon"]
    mc_trop = _mc_tropical(dt_utc, lat, lon)
    mc_sid = (mc_trop - ayanamsa) % 360
    bhava = _bhava_sripati(asc_lon, mc_sid)

    # ── Yogas y Mangal Dosha ──────────────────────────────────────────────
    yogas = _yogas(planets)
    mangal = _mangal_dosha(planets)

    return {
        "nombre": nombre,
        "nacimiento": {
            "fecha": fecha,
            "hora": hora,
            "ciudad": ciudad,
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "tz": tz_name,
            "utc": dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "ayanamsa_lahiri": round(ayanamsa, 4),
        },
        "d1": d1,
        "nakshatra_luna": moon_nak,
        "d9": d9,
        "d10": d10,
        "vimshottari_dasha": dasha,
        "sade_sati": sade_sati,
        "shad_bala": shad_bala,
        "ashtakavarga": ashtak,
        "karakas_jaimini": karakas,
        "karakas_jaimini_detalle": karakas_detalle,
        "karakamsha": karakamsha,
        "upapada_lagna": upapada,
        "doshas_ayurvedicos": doshas,
        "moon_chart": moon_chart,
        "bhava_sripati": bhava,
        "yogas": yogas,
        "mangal_dosha": mangal,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI de prueba / validación
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    resultado = get_birth_data(
        nombre="Nicolás Jiménez",
        fecha="2003-03-28",
        hora="08:07",
        ciudad="Bogotá, Colombia",
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
