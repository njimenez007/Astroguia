"""
System prompt, contexto enriquecido y bloques para la Carta Astral (Lectura de Primera Cita).
Basado en PLANTILLA_MAESTRA_Primera_Cita_v5.0 de Dario Jiménez Medina.
"""
import json
import re
from datetime import date as _date, datetime as _dt
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# TABLAS DE REFERENCIA
# ─────────────────────────────────────────────────────────────────────────────

NAKSHATRA_INFO: dict[str, dict] = {
    "Ashwini":           {"regente": "Ketu",     "deidad": "Ashvins",         "epiteto": "El Médico Veloz"},
    "Bharani":           {"regente": "Venus",     "deidad": "Yama",            "epiteto": "La Portadora"},
    "Krittika":          {"regente": "Sol",       "deidad": "Agni",            "epiteto": "La Cortadora"},
    "Rohini":            {"regente": "Luna",      "deidad": "Brahma",          "epiteto": "La Rojiza"},
    "Mrigashirsha":      {"regente": "Marte",     "deidad": "Soma",            "epiteto": "La Cabeza del Ciervo"},
    "Ardra":             {"regente": "Rahu",      "deidad": "Rudra",           "epiteto": "La Tormenta"},
    "Punarvasu":         {"regente": "Júpiter",   "deidad": "Aditi",           "epiteto": "El Retorno de la Luz"},
    "Pushya":            {"regente": "Saturno",   "deidad": "Brihaspati",      "epiteto": "El Nutridor"},
    "Ashlesha":          {"regente": "Mercurio",  "deidad": "Sarpa",           "epiteto": "La Abrazadora"},
    "Magha":             {"regente": "Ketu",      "deidad": "Pitrs",           "epiteto": "La Grande"},
    "Purva Phalguni":    {"regente": "Venus",     "deidad": "Bhaga",           "epiteto": "La Anterior"},
    "Uttara Phalguni":   {"regente": "Sol",       "deidad": "Aryaman",         "epiteto": "La Posterior"},
    "Hasta":             {"regente": "Luna",      "deidad": "Savitar",         "epiteto": "La Mano"},
    "Chitra":            {"regente": "Marte",     "deidad": "Vishvakarman",    "epiteto": "El Brillante"},
    "Swati":             {"regente": "Rahu",      "deidad": "Vayu",            "epiteto": "La Perla"},
    "Vishakha":          {"regente": "Júpiter",   "deidad": "Indra-Agni",      "epiteto": "La Bifurcada"},
    "Anuradha":          {"regente": "Saturno",   "deidad": "Mitra",           "epiteto": "El Seguidor de Radha"},
    "Jyeshtha":          {"regente": "Mercurio",  "deidad": "Indra",           "epiteto": "El Mayor"},
    "Mula":              {"regente": "Ketu",      "deidad": "Nirriti",         "epiteto": "La Raíz"},
    "Purva Ashadha":     {"regente": "Venus",     "deidad": "Apas",            "epiteto": "La Victoria Anterior"},
    "Uttara Ashadha":    {"regente": "Sol",       "deidad": "Vishvedevas",     "epiteto": "La Victoria Posterior"},
    "Shravana":          {"regente": "Luna",      "deidad": "Vishnu",          "epiteto": "El Oído"},
    "Dhanishtha":        {"regente": "Marte",     "deidad": "Ashta Vasus",     "epiteto": "La Más Rica"},
    "Shatabhisha":       {"regente": "Rahu",      "deidad": "Varuna",          "epiteto": "Cien Médicos"},
    "Purva Bhadrapada":  {"regente": "Júpiter",   "deidad": "Aja Ekapad",      "epiteto": "Los Pies Anteriores"},
    "Uttara Bhadrapada": {"regente": "Saturno",   "deidad": "Ahir Budhnya",    "epiteto": "Los Pies Posteriores"},
    "Revati":            {"regente": "Mercurio",  "deidad": "Pushan",          "epiteto": "La Próspera"},
}

SIGN_RULER = {
    "Aries": "Marte", "Tauro": "Venus", "Géminis": "Mercurio",
    "Cáncer": "Luna", "Leo": "Sol", "Virgo": "Mercurio",
    "Libra": "Venus", "Escorpio": "Marte", "Sagitario": "Júpiter",
    "Capricornio": "Saturno", "Acuario": "Saturno", "Piscis": "Júpiter",
}

SIGN_ELEMENT = {
    "Aries": "Fuego", "Leo": "Fuego", "Sagitario": "Fuego",
    "Tauro": "Tierra", "Virgo": "Tierra", "Capricornio": "Tierra",
    "Géminis": "Aire", "Libra": "Aire", "Acuario": "Aire",
    "Cáncer": "Agua", "Escorpio": "Agua", "Piscis": "Agua",
}

SIGN_QUALITY = {
    "Aries": "Cardinal (Chara)", "Cáncer": "Cardinal (Chara)",
    "Libra": "Cardinal (Chara)", "Capricornio": "Cardinal (Chara)",
    "Tauro": "Fija (Sthira)", "Leo": "Fija (Sthira)",
    "Escorpio": "Fija (Sthira)", "Acuario": "Fija (Sthira)",
    "Géminis": "Dual (Dvisvabhava)", "Virgo": "Dual (Dvisvabhava)",
    "Sagitario": "Dual (Dvisvabhava)", "Piscis": "Dual (Dvisvabhava)",
}

SIGN_APOLOGIA_SUBS = {
    "Aries":       ["El Ímpetu del Inicio", "La Nobleza de la Cornamenta", "El Sacrificio y la Renovación", "La Inocencia del Fuego"],
    "Tauro":       ["El Culto a la Estabilidad", "La Sensibilidad de la Piel", "La Fuerza del Silencio", "La Nobleza de la Terquedad"],
    "Géminis":     ["El Elogio de la Versatilidad", "La Dualidad Sagrada", "El Valor de la Palabra y el Juego", "La Mente como un Prisma"],
    "Cáncer":      ["El Caparazón", "El Andar de Lado", "Las Pinzas", "La Regencia de la Luna"],
    "Leo":         ["El Derecho a la Centralidad", "La Nobleza de la Melena", "El Rugido como Verdad", "El Corazón como Motor"],
    "Virgo":       ["La Pureza como Integridad", "El Sacrificio de la Observación", "El Ritual de lo Cotidiano", "La Inteligencia Práctica"],
    "Libra":       ["El Heroísmo del Punto Medio", "La Estética como Ética", "La Identidad en el Nosotros", "La Inteligencia de la Indecisión"],
    "Escorpio":    ["El Valor de Mirar la Sombra", "El Veneno como Medicina", "La Lealtad de la Entrega Total", "Las Tres Etapas"],
    "Sagitario":   ["La Flecha como Propósito", "La Naturaleza del Centauro", "El Elogio de la Verdad Desnuda", "La Sagrada Libertad del Viajero"],
    "Capricornio": ["El Ascenso Solitario", "La Cabra-Pez", "El Dominio sobre Cronos", "La Soledad del Soberano"],
    "Acuario":     ["El Agua que se Comparte", "El Derecho a la Diferencia", "La Fraternidad de los Iguales", "La Mente Relámpago"],
    "Piscis":      ["La Dualidad sin Conflicto", "La Fortaleza de la Rendición", "El Sacrificio de la Compasión", "El Sueño como Realidad Superior"],
}

DAY_PLANET = {
    "Monday": "Luna", "Tuesday": "Marte", "Wednesday": "Mercurio",
    "Thursday": "Júpiter", "Friday": "Venus", "Saturday": "Saturno", "Sunday": "Sol",
}
DAY_ES = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo",
}

SHAD_BALA_MINIMO = {
    "Sol": 6.5, "Luna": 6.0, "Marte": 5.0,
    "Mercurio": 7.0, "Júpiter": 6.5, "Venus": 5.5, "Saturno": 5.0,
}

SIGNS_ORDER = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
               "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]

BLOCK_TITLES = {
    1: "Datos Generales y Personalidad",
    2: "Esencia y Arquetipo del Lagna",
    3: "Nakshatras y Constitución Energética",
    4: "Arsenal Planetario y Deseos del Alma",
    5: "Los 8 Pilares del Destino",
}

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM = """\
Eres el Sistema Parashara Completo — astrólogo védico maestro con décadas de experiencia en la \
tradición Parampara del sur de la India. Estás generando la Lectura de Primera Cita (Carta Astral) \
para {nombre}.

REGLAS ABSOLUTAS:
• Usa EXCLUSIVAMENTE los datos del JSON proporcionado. No inventes ni supongas nada.
• Si un valor aparece como "—" o vacío, omítelo graciosamente.
• Tono: Gurú compasivo. Lenguaje accesible para no astrólogos, sin tecnicismos sin traducir. \
  Registro: Maestro – Guía – Inspirador. Cada frase debe motivar, iluminar y revelar.
• NO repitas conceptos ya desarrollados en bloques anteriores de esta misma lectura.
• Cumple los MÍNIMOS de líneas/profundidad obligatorios en cada sección.
• Sustituye todos los [VARIABLES] con los datos reales del JSON.
• Formato: Markdown. **Negritas** para conceptos clave. Tablas cuando se indiquen. Encabezados ##/###.
• Termina cada bloque con el marcador exacto: ✅ BLOQUE N COMPLETADO — LISTO PARA BLOQUE N+1
"""

# ─────────────────────────────────────────────────────────────────────────────
# CONTEXTO ENRIQUECIDO
# ─────────────────────────────────────────────────────────────────────────────

def prepare_carta_context(birth_data: dict, nombre: str) -> dict:
    """Construye el contexto completo y enriquecido para los 5 bloques."""
    nac = birth_data.get("nacimiento", {})
    d1  = birth_data.get("d1", {})

    lagna_signo = d1.get("lagna", {}).get("signo", "")
    lagna_grado = d1.get("lagna", {}).get("grado", "")

    # Planets dict
    planets: dict[str, dict] = {p["planeta"]: p for p in d1.get("planetas", [])}

    # --- Día de nacimiento ---
    fecha_str = nac.get("fecha", "")
    dia_semana, planeta_dia = "N/A", "N/A"
    fecha_dt = None
    try:
        fecha_dt = _dt.strptime(fecha_str, "%Y-%m-%d")
        day_en = fecha_dt.strftime("%A")
        dia_semana = DAY_ES.get(day_en, day_en)
        planeta_dia = DAY_PLANET.get(day_en, "N/A")
    except Exception:
        pass

    # --- Edad ---
    edad = "N/A"
    try:
        hoy = _date.today()
        nb  = fecha_dt.date()
        edad = hoy.year - nb.year - ((hoy.month, hoy.day) < (nb.month, nb.day))
    except Exception:
        pass

    # --- Lagna Tropical ---
    tropical_lagna = "N/A"
    try:
        ayanamsa = nac.get("ayanamsa_lahiri", 23.9)
        m = re.match(r"(\d+)°", lagna_grado)
        deg = int(m.group(1)) if m else 0
        idx = SIGNS_ORDER.index(lagna_signo)
        total = (idx * 30 + deg + ayanamsa) % 360
        tropical_lagna = SIGNS_ORDER[int(total // 30)]
    except Exception:
        pass

    # --- Regente del Lagna ---
    regente_lagna = SIGN_RULER.get(lagna_signo, "")
    rp = planets.get(regente_lagna, {})

    # --- Nakshatras (Lagna, Luna, Sol) ---
    def _nk(planet_key: str) -> dict:
        p = planets.get(planet_key, {})
        nk_name = p.get("nakshatra", "")
        info = NAKSHATRA_INFO.get(nk_name, {})
        return {
            "nombre":   nk_name,
            "epiteto":  info.get("epiteto", ""),
            "pada":     p.get("pada", ""),
            "signo":    p.get("signo", ""),
            "grado":    p.get("grado", ""),
            "regente":  info.get("regente", ""),
            "deidad":   info.get("deidad", ""),
        }

    nk_lagna = _nk("Lagna")
    nk_luna  = _nk("Luna")
    nk_sol   = _nk("Sol")
    # Enriquecer luna con datos del motor
    nk_luna_rich = birth_data.get("nakshatra_luna", {})
    if nk_luna_rich.get("regente"):
        nk_luna["regente"] = nk_luna_rich["regente"]
        nk_luna["deidad"]  = nk_luna_rich.get("deidad", nk_luna["deidad"])

    # --- Shadbala enriquecida ---
    shad_bala_raw = birth_data.get("shad_bala", [])
    shad_sorted   = sorted(shad_bala_raw, key=lambda p: p.get("rupas", 0), reverse=True)
    shad_bala: list[dict] = []
    for rank, p in enumerate(shad_sorted, 1):
        pname   = p["planeta"]
        minimo  = SHAD_BALA_MINIMO.get(pname, 5.0)
        rupas   = p.get("rupas", 0)
        dignidad_d1 = planets.get(pname, {}).get("dignidad", "—")
        shad_bala.append({
            "rango":             rank,
            "planeta":           pname,
            "rupas":             round(rupas, 3),
            "minimo_requerido":  minimo,
            "pct_minimo":        round(rupas / minimo * 100, 1),
            "sobre_minimo":      rupas >= minimo,
            "dignidad_d1":       dignidad_d1,
            "ishta_phala":       round(p.get("ishta_phala", 0), 2),
            "kashta_phala":      round(p.get("kashta_phala", 0), 2),
        })

    # --- Karakas Jaimini con posición ---
    karakas_raw = birth_data.get("karakas_jaimini", {})
    _karaka_map = [
        ("Atmakaraka (AK)",    "AK",  "Propósito del alma — lección central de vida"),
        ("Amatyakaraka (AMK)", "AMK", "Carrera, vocación y apoyo externo"),
        ("Bhratrikaraka (BK)", "BK",  "Hermanos y valentía"),
        ("Matrikaraka (MK)",   "MK",  "Madre, mente e intuición"),
        ("Putrakaraka (PK)",   "PK",  "Hijos y creatividad"),
        ("Gnatikaraka (GK)",   "GK",  "Karma colectivo y competidores"),
        ("Darakaraka (DK)",    "DK",  "Pareja y relaciones íntimas"),
    ]
    karakas: list[dict] = []
    for full_name, abrev, desc in _karaka_map:
        planeta = karakas_raw.get(full_name, "")
        pd = planets.get(planeta, {})
        karakas.append({
            "karaka":      full_name,
            "abrev":       abrev,
            "planeta":     planeta,
            "signo":       pd.get("signo", ""),
            "casa":        pd.get("casa", ""),
            "grado":       pd.get("grado", ""),
            "dignidad":    pd.get("dignidad", "—"),
            "retrograde":  pd.get("retrograde", False),
            "descripcion": desc,
        })

    # --- Casas Whole Sign (señor + ocupantes) ---
    lagna_idx = SIGNS_ORDER.index(lagna_signo) if lagna_signo in SIGNS_ORDER else 0
    casas: dict[str, dict] = {}
    for h in range(1, 13):
        sign_h = SIGNS_ORDER[(lagna_idx + h - 1) % 12]
        lord   = SIGN_RULER.get(sign_h, "")
        lp     = planets.get(lord, {})
        occupants = [
            {"planeta": p["planeta"], "grado": p["grado"],
             "dignidad": p["dignidad"], "retro": p["retrograde"]}
            for p in d1.get("planetas", [])
            if p.get("casa") == h and p["planeta"] != "Lagna"
        ]
        casas[str(h)] = {
            "signo":           sign_h,
            "senor":           lord,
            "senor_en_casa":   lp.get("casa", ""),
            "senor_en_signo":  lp.get("signo", ""),
            "senor_grado":     lp.get("grado", ""),
            "senor_dignidad":  lp.get("dignidad", "—"),
            "senor_retro":     lp.get("retrograde", False),
            "ocupantes":       occupants,
        }

    # --- Dasha actual ---
    from prompts.gancho import _current_dasha
    dasha_actual = _current_dasha(birth_data, _date.today().isoformat())

    return {
        "nombre":              nombre,
        "nacimiento": {
            "fecha":   fecha_str,
            "hora":    nac.get("hora", ""),
            "ciudad":  nac.get("ciudad", ""),
        },
        "edad_actual":         edad,
        "dia_semana":          dia_semana,
        "planeta_regente_dia": planeta_dia,
        "signo_tropical_lagna": tropical_lagna,
        "lagna": {
            "signo":     lagna_signo,
            "grado":     lagna_grado,
            "elemento":  SIGN_ELEMENT.get(lagna_signo, ""),
            "cualidad":  SIGN_QUALITY.get(lagna_signo, ""),
            "apologia_sub_apartados": SIGN_APOLOGIA_SUBS.get(lagna_signo, []),
            "regente":   regente_lagna,
            "regente_en_signo":   rp.get("signo", ""),
            "regente_en_casa":    rp.get("casa", ""),
            "regente_grado":      rp.get("grado", ""),
            "regente_dignidad":   rp.get("dignidad", "—"),
            "regente_retrograde": rp.get("retrograde", False),
        },
        "planetas_d1":     d1.get("planetas", []),
        "nakshatra_lagna": nk_lagna,
        "nakshatra_luna":  nk_luna,
        "nakshatra_sol":   nk_sol,
        "doshas":          birth_data.get("doshas_ayurvedicos", {}),
        "shad_bala":       shad_bala,
        "karakas_jaimini": karakas,
        "yogas":           birth_data.get("yogas", []),
        "mangal_dosha":    birth_data.get("mangal_dosha", {}),
        "casas":           casas,
        "sade_sati":       birth_data.get("sade_sati", {}),
        "dasha_actual":    dasha_actual,
        "d9_lagna":        birth_data.get("d9", {}).get("lagna", {}),
    }

# ─────────────────────────────────────────────────────────────────────────────
# CONTEXTO POR BLOQUE (sólo lo relevante)
# ─────────────────────────────────────────────────────────────────────────────

def get_block_context(num: int, ctx: dict) -> dict:
    """Devuelve el subconjunto de contexto relevante para el bloque indicado."""
    base = {"nombre": ctx["nombre"]}
    if num == 1:
        return {**base,
            "nacimiento": ctx["nacimiento"],
            "edad_actual": ctx["edad_actual"],
            "dia_semana": ctx["dia_semana"],
            "planeta_regente_dia": ctx["planeta_regente_dia"],
            "signo_tropical_lagna": ctx["signo_tropical_lagna"],
            "lagna": {k: ctx["lagna"][k] for k in
                      ["signo","grado","regente","regente_en_signo","regente_en_casa"]},
            "nakshatra_lagna": ctx["nakshatra_lagna"],
            "yogas": ctx["yogas"],
            "planetas_d1": ctx["planetas_d1"],
        }
    if num == 2:
        return {**base, "lagna": ctx["lagna"]}
    if num == 3:
        return {**base,
            "nakshatra_lagna": ctx["nakshatra_lagna"],
            "nakshatra_luna":  ctx["nakshatra_luna"],
            "nakshatra_sol":   ctx["nakshatra_sol"],
            "doshas":          ctx["doshas"],
            "lagna":           {k: ctx["lagna"][k] for k in ["signo","grado","regente_en_casa"]},
            "planetas_d1":     ctx["planetas_d1"],
        }
    if num == 4:
        return {**base,
            "shad_bala":       ctx["shad_bala"],
            "karakas_jaimini": ctx["karakas_jaimini"],
            "planetas_d1":     ctx["planetas_d1"],
        }
    if num == 5:
        return {**base,
            "lagna":           ctx["lagna"],
            "casas":           ctx["casas"],
            "planetas_d1":     ctx["planetas_d1"],
            "sade_sati":       ctx["sade_sati"],
            "dasha_actual":    ctx["dasha_actual"],
            "yogas":           ctx["yogas"],
            "karakas_jaimini": ctx["karakas_jaimini"],
            "d9_lagna":        ctx["d9_lagna"],
        }
    return ctx


# ─────────────────────────────────────────────────────────────────────────────
# BLOQUES DE INSTRUCCIONES (adaptados de PLANTILLA_MAESTRA_Primera_Cita_v5.0)
# ─────────────────────────────────────────────────────────────────────────────

def build_block_message(num: int, block_ctx: dict) -> str:
    ctx_json = json.dumps(block_ctx, ensure_ascii=False, indent=2)
    nombre   = block_ctx["nombre"]

    if num == 1:
        return f"""BLOQUE 1 DE 5 — DATOS GENERALES Y PERSONALIDAD
Secciones: Paso 0 · I · II

REGLA DE EXTENSIÓN — OBLIGATORIA
Estás generando la Lectura de Primera Cita para {nombre}. Este es el BLOQUE 1 DE 5.
• Desarrolla ÚNICAMENTE las secciones del Bloque 1 con máxima extensión y profundidad.
• Ninguna sección puede resumirse por limitaciones de longitud.
• Ningún dato puede suponerse — si no está en el JSON, indicarlo explícitamente.
Al terminar escribir: ✅ BLOQUE 1 COMPLETADO — LISTO PARA BLOQUE 2

---

🔍 PASO 0 — INSTRUCCIÓN GENERAL

Actúa como un Astrólogo Védico experto (Gurú/Maestro de Parashara) y genera la Lectura de
Primera Cita para {nombre} usando los datos del JSON adjunto.
Extrae TODOS los datos del JSON. El objetivo es un análisis profundo y motivador.
Sigue rigurosamente la estructura de las secciones a continuación.

TONO: Gurú compasivo, lenguaje accesible para no astrólogos, sin tecnicismos sin traducir,
con metáforas espirituales. Registro: Maestro – Guía – Inspirador.
PRIMORDIAL: Evitar durante los 5 bloques la repetición de conceptos.

---

📋 SECCIÓN I — INTRODUCCIÓN Y DATOS GENERALES

**1. Datos Esenciales de Nacimiento**

Genera esta tabla completa con los valores del JSON:

| Concepto | Detalle |
|---|---|
| Nombre del consultante | (del JSON: nombre) |
| Fecha de nacimiento | (del JSON: nacimiento.fecha) |
| Hora exacta de nacimiento | (del JSON: nacimiento.hora) |
| Lugar de nacimiento | (del JSON: nacimiento.ciudad) |
| Edad al momento de la lectura | (del JSON: edad_actual) |
| Día de nacimiento | (del JSON: dia_semana) |
| Planeta regente del día | (del JSON: planeta_regente_dia) |
| Signo Astrología Tropical | (del JSON: signo_tropical_lagna) |
| Lagna Védico (Ascendente) | (del JSON: lagna.signo + lagna.grado) |
| Regente del Ascendente | (del JSON: lagna.regente) |
| Nakshatra del Lagna | (del JSON: nakshatra_lagna.nombre, Pada del JSON: nakshatra_lagna.pada) |

Mantener el texto comparativo fijo a continuación (copiarlo textualmente):

| ITEM | Astrología Occidental | Astrología Védica |
|---|---|---|
| Sistema de Medición | Se basa en el zodiaco tropical, alineado con las estaciones del año. Toma como referencia el equinoccio de primavera. Día de nacimiento. | Originaria de la antigua India, utiliza el zodiaco sideral, basado en la posición real de las constelaciones. Hora de nacimiento. |
| Enfoque | Orientado hacia la psicología, la personalidad y la expresión individual en el mundo moderno. | Enfoque profundo y espiritual, integrando karma, dharma y ciclos evolutivos del alma. Jyotish: "la ciencia de la luz". |

---

**2. La Revelación (Hook Inicial)**

Usar el siguiente encabezado fijo:
"Antes de entrar a los pilares de tu carta, {nombre}, quiero mostrarte algo muy especial: Tu mapa natal tiene una configuración poco común. Hay una concentración de planetas fuertes y casas bien posicionados con una energía profundamente protectora. Tu mayor bendición se encuentra tejida en el sagrado ámbito de:"

→ Elaborar un análisis de las situaciones más positivas e importantes de la carta usando los yogas, planetas con alta dignidad, y posiciones de fuerza del JSON. Mínimo 8 líneas.

---

🌟 SECCIÓN II — ESENCIA DE LA PERSONALIDAD: EL DÍA DE NACIMIENTO

INSTRUCCIÓN CRÍTICA: Esta sección se centra ÚNICAMENTE en la contribución del día de nacimiento.
No superponer conceptos con las secciones del Bloque 2 (signo, regente, elemento).

**La Influencia del Día de Nacimiento**
Nacido(a) en {nombre}: usar dia_semana del JSON, regido por planeta_regente_dia del JSON.
Describir los aportes que genera en su personalidad haber nacido ese día.
Cómo el planeta regente del día modela el carácter, la energía vital y el ritmo natural.
Mínimo 6 líneas.

---
DATOS ASTROLÓGICOS (usar exclusivamente estos datos):
```json
{ctx_json}
```
"""

    if num == 2:
        lagna = block_ctx.get("lagna", {})
        subs  = " · ".join(lagna.get("apologia_sub_apartados", []))
        return f"""BLOQUE 2 DE 5 — ESENCIA Y ARQUETIPO
Secciones: III · IV · V

REGLA DE EXTENSIÓN — OBLIGATORIA
Este es el BLOQUE 2 DE 5. El Bloque 1 ya fue generado — mantener coherencia total.
• Desarrolla ÚNICAMENTE las secciones III a V con máxima extensión y profundidad.
• IMPERATIVO: Cada subcapítulo tiene su CONTRIBUCIÓN ÚNICA — eliminar superposición.
• Mínimo 20 líneas para la Apología del Signo.
Al terminar escribir: ✅ BLOQUE 2 COMPLETADO — LISTO PARA BLOQUE 3

---

♈ SECCIÓN III — APOLOGÍA DEL SÍMBOLO: EL ARQUETIPO DEL LAGNA VÉDICO

El Lagna védico de {nombre} es **{lagna.get("signo","")}**.

Desarrollar la apología completa del signo **{lagna.get("signo","")}** con sus 4 sub-apartados OBLIGATORIOS:
{subs}

Cada sub-apartado debe tener:
• Título en **negrita** como encabezado
• Mínimo 4-5 líneas de desarrollo narrativo con metáforas espirituales
• Relación directa con la personalidad de {nombre}
Cerrar con una frase poética integradora del signo. Total mínimo: 20 líneas.

---

🪐 SECCIÓN IV — REGENTE DEL LAGNA: {lagna.get("regente","")} en {lagna.get("regente_en_signo","")}, Casa {lagna.get("regente_en_casa","")}

Analizar **{lagna.get("regente","")}** como regente del Lagna y sus aportes directos a la personalidad de {nombre}.

Requerimientos:
• Naturaleza general del planeta {lagna.get("regente","")} (qué rige, qué representa)
• Ubicación específica: {lagna.get("regente_grado","")} {lagna.get("regente_en_signo","")} en Casa {lagna.get("regente_en_casa","")}
  y cómo esta ubicación modifica la personalidad — MÍNIMO 4 características
• Usar formato: **Punto en negrita** + breve descripción
• NO repetir conceptos de la Apología del Signo (Sección III)

---

🌍 SECCIÓN V — ELEMENTO Y CUALIDAD DEL LAGNA

**5A. Características del Elemento {lagna.get("elemento","")}**

Analizar el elemento **{lagna.get("elemento","")}** del Lagna {lagna.get("signo","")} y su impacto en la personalidad.
Mínimo 4 características. Formato: **Punto en negrita** + descripción.
Conectar con necesidades y motivaciones fundamentales de {nombre}.

**5B. Características de la Cualidad {lagna.get("cualidad","")}**

Analizar la cualidad **{lagna.get("cualidad","")}** y cómo afecta el temperamento y comportamiento.
Mínimo 4 características. Formato: **Punto en negrita** + descripción.
NO repetir conceptos de secciones anteriores.

**5C. Frase Didáctica del Bloque II**

Una sola oración poética que sintetice la personalidad de {nombre} integrando signo, regente, elemento y cualidad.

---
DATOS (usar exclusivamente estos):
```json
{ctx_json}
```
"""

    if num == 3:
        nk_l = block_ctx.get("nakshatra_lagna", {})
        nk_m = block_ctx.get("nakshatra_luna",  {})
        nk_s = block_ctx.get("nakshatra_sol",   {})
        return f"""BLOQUE 3 DE 5 — NAKSHATRAS Y CONSTITUCIÓN ENERGÉTICA
Secciones: VI · VII

REGLA DE EXTENSIÓN — OBLIGATORIA
Este es el BLOQUE 3 DE 5. Los Bloques 1 y 2 ya fueron generados — mantener coherencia total.
• Cada Nakshatra (Ascendente, Luna, Sol) debe desarrollarse con sus sub-apartados completos.
• El análisis de Doshas debe integrar datos técnicos con interpretación narrativa.
Al terminar escribir: ✅ BLOQUE 3 COMPLETADO — LISTO PARA BLOQUE 4

---

🌑 SECCIÓN VI — LA MANSIÓN LUNAR Y LA CONSTITUCIÓN ENERGÉTICA (NAKSHATRAS)

Introducción (3-4 líneas):
Las Nakshatras son las "Mansiones de la Luna" — 27 constelaciones lejanas que revelan el sistema
operativo más profundo de la conciencia. La carta de {nombre} revela una configuración fascinante
gobernada por el poder de sus tres estrellas principales.

---

**1. Nakshatra del Ascendente: {nk_l.get("nombre","")} — "{nk_l.get("epiteto","")}"**

| Campo | Variable |
|---|---|
| Ubicación | {nk_l.get("grado","")} |
| Regente Planetario | {nk_l.get("regente","")} |
| Deidad | {nk_l.get("deidad","")} |
| Pada | {nk_l.get("pada","")} |

Desarrollar OBLIGATORIAMENTE estos 4 sub-apartados para el Nakshatra {nk_l.get("nombre","")}:

**A. Significado Clave y Traducción** (mínimo 6 líneas):
Qué significa este Nakshatra en la tradición védica, su símbolo, su historia.

**B. Energías Particulares** (mínimo 6 líneas):
Dones, talentos y formas de expresión que este Nakshatra le da al Ascendente de {nombre}.

**C. Retos y Desafíos — La Sombra** (mínimo 4 líneas):
Los patrones de sombra o desafíos de este Nakshatra en el cuerpo y la identidad.

**D. Profesiones y Talentos Ocultos** (mínimo 4 líneas):
Áreas de destaque, vocaciones y talentos ocultos que este Nakshatra revela.

---

**2. Nakshatra de la Luna (Janma Nakshatra): {nk_m.get("nombre","")} — "{nk_m.get("epiteto","")}"**

| Campo | Variable |
|---|---|
| Ubicación | {nk_m.get("grado","")} |
| Regente Planetario | {nk_m.get("regente","")} |
| Deidad | {nk_m.get("deidad","")} |
| Pada | {nk_m.get("pada","")} |

**El Significado** — La mente emocional, instintos y forma de sentir seguridad (mínimo 5 líneas):
La naturaleza interna más profunda de {nombre} según {nk_m.get("nombre","")}.

**El Símbolo** — Cualidad psicológica y habilidad emocional derivada (mínimo 4 líneas):
El símbolo de este Nakshatra y lo que revela sobre la vida emocional de {nombre}.

**La Conexión Kármica** — Memorias del alma y necesidad instintiva (mínimo 4 líneas):
El patrón kármico que {nombre} trae de vidas anteriores según este Nakshatra.

---

**3. Nakshatra del Sol: {nk_s.get("nombre","")} — "{nk_s.get("epiteto","")}"**

| Campo | Variable |
|---|---|
| Ubicación | {nk_s.get("grado","")} |
| Regente Planetario | {nk_s.get("regente","")} |
| Deidad | {nk_s.get("deidad","")} |
| Pada | {nk_s.get("pada","")} |

**El Arquetipo** — Deidad y destino del área de la casa del Sol (mínimo 5 líneas):
El propósito del alma y la proyección del ego de {nombre} según {nk_s.get("nombre","")}.

**La Proyección** — Imagen pública y satisfacción del ego (mínimo 4 líneas):
Cómo {nombre} expresa su identidad al mundo y en qué área brilla.

---

**4. Tabla de Fortalezas y Desafíos**

| Nakshatra | Fortaleza (Shakti) | Desafío (Dosha) |
|---|---|---|
| {nk_l.get("nombre","")} (Cuerpo/Lagna) | [Fortaleza física o de identidad — del análisis anterior] | [Reto de personalidad o salud] |
| {nk_m.get("nombre","")} (Mente/Luna) | [Talento emocional o mental] | [Trampa emocional o mental] |
| {nk_s.get("nombre","")} (Alma/Sol) | [Talento del alma o liderazgo] | [Trampa del ego] |

---

🧬 SECCIÓN VII — ANÁLISIS DE DOSHAS (CONSTITUCIÓN BIO-ENERGÉTICA)

**Notas Técnicas**
Usar los valores del JSON: lagna.signo, nakshatra_luna, planetas_d1 (Luna, Marte, Rahu/Ketu).

**Constitución predominante**: usar el campo doshas.predominante del JSON.
**Distribución**: usar doshas.breakdown_pct del JSON.

Desarrollar:
1. Interpretación narrativa del perfil Dosha (mínimo 6 líneas): Cómo se manifiesta esta constitución en el temperamento, energía vital y forma de relacionarse de {nombre}.
2. Diagnóstico de salud (mínimo 5 líneas): Cómo somatiza el estrés, qué zonas del cuerpo son más sensibles, cómo afectan las casas I, VI y VIII.
3. Recomendaciones Védicas Prácticas: tipo de ejercicio, dieta según Dosha, rutinas de meditación/pranayama, día de ayuno o descanso según regente del Lagna.
4. Síntesis (2 líneas): Frase final sobre el equilibrio óptimo para {nombre}.

**Conclusión del Bloque III — Frase Didáctica**
Una sola oración poética que sintetice la mezcla de los tres astros (Lagna, Luna, Sol) de {nombre}.

---
DATOS (usar exclusivamente estos):
```json
{ctx_json}
```
"""

    if num == 4:
        return f"""BLOQUE 4 DE 5 — ARSENAL PLANETARIO Y DESEOS DEL ALMA
Secciones: VIII · IX

REGLA DE EXTENSIÓN — OBLIGATORIA
Este es el BLOQUE 4 DE 5. Los Bloques 1, 2 y 3 ya fueron generados — mantener coherencia total.
• Usar los valores del JSON para las tablas — no estimar.
• Diferencia entre fuerza mecánica (Shadbala) y rol kármico (Karakas) debe quedar clara.
Al terminar escribir: ✅ BLOQUE 4 COMPLETADO — LISTO PARA BLOQUE 5

---

📊 SECCIÓN VIII — ANÁLISIS DE FUERZA PLANETARIA (SHADBALA)

Un planeta sin fuerza real no produce resultados aunque el período sea favorable.

**Tabla de Fortaleza de TODOS los Planetas (Contexto Comparativo)**

Usando los datos de shad_bala del JSON, genera esta tabla completa:

| Planeta | Rupas | Mínimo Req. | % del Mínimo | Rango | Dignidad D1 | Estado |
|---|---|---|---|---|---|---|
(llenar con todos los planetas del JSON shad_bala — ordenados por rango)

**El Comandante Supremo** (planeta con Rango #1):
Identificar el planeta más fuerte y explicar su significado para {nombre} — mínimo 4 líneas.
¿Qué áreas de vida protege y potencia?

**Los Servidores del Alma** (planetas sobre el mínimo requerido):
Identificar y desarrollar las fortalezas de los planetas bien posicionados — mínimo 4 líneas.

**Los Planetas en Desafío** (planetas por debajo del mínimo requerido):
La interpretación debe centrarse en que su suerte en estas áreas NO es automática y debe cultivarse conscientemente.
Mínimo 4 líneas. Tono: motivador, no fatalista.

**Análisis Narrativo Integrador del Shadbala** (mínimo 8 líneas):
Traducir los números a la vida real de {nombre}: ¿Qué puede lograr fácilmente? ¿Qué requiere más esfuerzo consciente?
¿Cómo usar sus planetas fuertes para compensar los débiles?

---

👑 SECCIÓN IX — LOS ROLES DEL ALMA (JAIMINI CHARA KARAKAS)

Los Karakas son los "actores" del drama del alma — cada planeta juega un rol kármico específico.

Usando los datos de karakas_jaimini del JSON:

**Atmakaraka (AK) — El Propósito del Alma**
Identificar el planeta AK del JSON y describir su lección fundamental para esta vida.
¿Qué debe aprender, desarrollar y trascender {nombre}? Mínimo 5 líneas.

**Amatyakaraka (AMK) — El Ministro del Alma**
Describir el rol del AMK en la carrera y vocación de {nombre}. Mínimo 4 líneas.

**Darakaraka (DK) — La Pareja del Alma**
Describir la cualidad de la pareja kármica ideal para {nombre}. Mínimo 4 líneas.

**Tabla Resumen de Karakas**

| Karaka | Abrev. | Planeta | Signo | Casa | Descripción del Rol |
|---|---|---|---|---|---|
(llenar con todos los karakas del JSON karakas_jaimini)

**Síntesis del Bloque IV — Frase Didáctica**
Párrafo (mínimo 6 líneas) fusionando Shadbala con Karakas: ¿Cómo sirve la fuerza mecánica de los planetas al propósito kármico del alma de {nombre}?
Cerrar con una frase poética que sintetice el arsenal planetario y el propósito del alma.

---
DATOS (usar exclusivamente estos):
```json
{ctx_json}
```
"""

    if num == 5:
        return f"""BLOQUE 5 DE 5 — LOS 8 PILARES DEL DESTINO
Secciones: X · XI · XII · XIII · XIV · XV · XVI · XVII

REGLA DE EXTENSIÓN — OBLIGATORIA — BLOQUE FINAL
Este es el BLOQUE 5 DE 5. Integra todo lo analizado en los 4 bloques anteriores.
• CADA pilar debe tener MÍNIMO 8 LÍNEAS de desarrollo real — no viñetas sueltas.
• Incluir Notas Técnicas al inicio de cada pilar justificando la interpretación.
• Responder las preguntas específicas de cada pilar.
• Cerrar CADA pilar con una "Frase de Poder" didáctica e inspiradora.
• NO repetir conceptos de bloques anteriores — esta es la aplicación práctica.
Al terminar escribir: ✅ LECTURA DE PRIMERA CITA COMPLETADA

Los datos para los 8 pilares están en casas, planetas_d1, karakas_jaimini, sade_sati, dasha_actual del JSON.

---

🏛️ LOS 8 PILARES DEL DESTINO

REGLAS DE ORO:
• Extraer datos exclusivamente del JSON
• No repetir conceptos de bloques anteriores
• Cada pilar es una unidad independiente de análisis
• Lenguaje accesible y motivador — Gurú compasivo

---

**PILAR 1: Dharma y Propósito de Vida 🌟**
Notas Técnicas: Analizar Atmakaraka (del JSON karakas_jaimini), Rahu (posición del JSON), stelliums.
Preguntas: ¿Cuál es el propósito del Alma? ¿Qué misión tiene en esta vida? ¿Cómo cumplir su Dharma?
Mínimo 8 líneas. Cerrar con: **Frase de Poder del Pilar 1**

**PILAR 2: Karma y Deudas del Pasado ⚖️**
Notas Técnicas: Casa 5 (señor y ocupantes del JSON casas["5"]), Ketu (posición del JSON).
Preguntas: ¿Cuál es su mayor deuda kármica? ¿Qué talento innato trae ya aprendido?
Mínimo 8 líneas. Cerrar con: **Frase de Poder del Pilar 2**

**PILAR 3: Profesión, Vocación y Contribución 💼**
Notas Técnicas: Regente Casa 10, Casa 3 y Casa 11 (del JSON casas).
Preguntas: ¿En qué áreas puede prosperar? ¿Estilo de trabajo ideal? ¿Cómo hacer del trabajo un camino espiritual?
Mínimo 8 líneas. Cerrar con: **Frase de Poder del Pilar 3**

**PILAR 4: Dinero y Estabilidad Financiera 💰**
Notas Técnicas: Luna (casa del JSON), Rahu (casa del JSON), Júpiter (posición y dignidad del JSON).
Preguntas: ¿Cómo lograr estabilidad financiera? ¿De dónde provienen los ingresos? ¿Qué obstáculos evitar?
Mínimo 8 líneas. Cerrar con: **Frase de Poder del Pilar 4**

**PILAR 5: Matrimonio y Pareja 💍**
Notas Técnicas: Casa 7 (señor y ocupantes del JSON casas["7"]), Venus y Júpiter (posiciones del JSON).
Preguntas: ¿Cómo será la pareja ideal? ¿Qué karma trae en relaciones? ¿Cómo armonizar vínculos?
Mínimo 8 líneas. Cerrar con: **Frase de Poder del Pilar 5**

**PILAR 6: Hijos y Descendencia 👶**
Notas Técnicas: Casa 5 (señor y ocupantes del JSON casas["5"]), Júpiter (posición del JSON).
Preguntas: ¿Tendencia hacia los hijos? ¿Qué tipo de relación con ellos? ¿Karma paternal/maternal?
Mínimo 8 líneas. Cerrar con: **Frase de Poder del Pilar 6**

**PILAR 7: Salud y Longevidad 🏥**
Notas Técnicas: Ascendente (del JSON lagna), Casa 6 (señor y ocupantes del JSON casas["6"]), Luna (posición).
Preguntas: ¿Órganos o sistemas más sensibles? ¿Principal causa de desequilibrio? ¿Qué prácticas ayudan más?
Mínimo 8 líneas. Cerrar con: **Frase de Poder del Pilar 7**

**PILAR 8: Espiritualidad y Trascendencia 🕉️**
Notas Técnicas: Ketu (posición del JSON), Sol (casa del JSON), Casa 12 (señor del JSON casas["12"]).
Preguntas: ¿Qué espiritualidad sirve más? ¿Cómo alcanzar Moksha? ¿Mayor don espiritual? ¿Mayor desafío?
Mínimo 8 líneas. Cerrar con: **Frase de Poder del Pilar 8**

---

🔱 CIERRE DE LA LECTURA DE PRIMERA CITA

Generar un cierre integrador que:
• Sintetice los 5 Bloques en una visión cohesiva de {nombre}
• Resalte las mayores fortalezas y el propósito de vida identificado
• Termine con una invitación inspiradora hacia el autoconocimiento
Mínimo 10 líneas.

---
DATOS (usar exclusivamente estos):
```json
{ctx_json}
```
"""

    return f"Bloque {num} no definido."
