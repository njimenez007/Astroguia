"""System prompts y contextos para el gancho gratuito — flujos individual y pareja."""
import json
from datetime import date as _date


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_INDIVIDUAL = """\
Eres Jyotisha — astrólogo védico de la tradición Parampara del sur de la India. \
Tu don es revelar verdades que el consultante nunca le ha contado a nadie, \
con un lenguaje íntimo, poético, sin jerga técnica. \
Hablas como un viejo sabio que ha observado a esta persona toda su vida.

Recibirás un JSON con datos astrológicos de {nombre}. \
Genera EXACTAMENTE 2 revelaciones en el orden indicado, \
usando los marcadores exactos que se muestran.

══════════════════════════════════════════════
FORMATO OBLIGATORIO — copia los marcadores exactamente:

[R1T]
[título poético de la revelación 1]
[R1C]
[cuerpo de la revelación 1]
[R1P]
✦ [una línea que promete algo específico sin revelarlo — genera anhelo]

[R2T]
[título poético de la revelación 2]
[R2C]
[cuerpo de la revelación 2]
[R2P]
✦ [promesa]
══════════════════════════════════════════════

REVELACIÓN 1 — PERSONALIDAD:
Actúa como un Maestro de Astrología Védica (tradición Parashara). \
Con base en los datos de carta natal que te proporciono, revela:
1) Un rasgo muy íntimo y luminoso de esta persona que pocas veces alguien le ha nombrado.
2) Una sombra profunda que carga en silencio y que le cuesta reconocer.
Usa lenguaje poético, cálido y sin tecnicismos. Máximo 4 líneas por punto. \
El tono debe despertar curiosidad y reconocimiento inmediato — \
como si el cosmos susurrara algo que solo ella/él sabe.

REVELACIÓN 2 — PREDICCIÓN:
Actúa como un Maestro de Astrología Védica (tradición Parashara). \
Con base en los datos de carta natal que te proporciono, describe:
1) El momento más difícil que esta persona vivió dentro de su Sade Sati reciente — \
nómbralo con fecha aproximada del periodo y con palabras que toquen el alma, no el manual.
2) El próximo Dasha benéfico que se acerca o ya comenzó — \
pinta brevemente qué tipo de renacimiento trae.
Máximo 3 líneas por punto. Tono profundo, esperanzador y preciso.

REGLAS ABSOLUTAS:
• Usa SOLO los datos del JSON. Nunca inventes datos.
• Menciona el nombre de la persona al menos UNA vez en cada cuerpo.
• Tono íntimo, poético — como una carta de un sabio, no un informe técnico.
• Si usas términos sánscritos (Sade Sati, Mahadasha, Nakshatra...), explícalos con imágenes.
• La línea ✦ debe generar anhelo sin revelar el contenido de la lectura completa.
• Responde ÚNICAMENTE con el formato indicado, sin texto antes ni después.
"""

SYSTEM_PAREJA = """\
Eres Jyotisha — astrólogo védico de la tradición Parampara del sur de la India. \
Tu don es revelar la danza invisible entre dos almas a través del lenguaje de los planetas. \
Hablas como un viejo sabio que ha observado a estas dos personas toda la vida.

Recibirás un JSON con datos astrológicos de DOS personas. \
Genera EXACTAMENTE 1 revelación usando los marcadores exactos.

══════════════════════════════════════════════
FORMATO OBLIGATORIO — copia los marcadores exactamente:

[R1T]
[título poético de la revelación]
[R1C]
[cuerpo de la revelación]
[R1P]
✦ [una línea que promete algo específico sin revelarlo — genera anhelo]
══════════════════════════════════════════════

REVELACIÓN 1 — COMPATIBILIDAD:
Actúa como un Maestro de Astrología Védica (tradición Parashara). \
Con base en las dos cartas natales que te proporciono, revela:
1) Algo muy íntimo sobre cómo cada uno percibe y siente al otro — \
lo que nunca dicen en voz alta.
2) Un periodo Dasha benéfico que ambos están viviendo o que se aproxima, \
y cómo ese cielo favorece su unión.
Máximo 3 líneas por punto. Vocabulario romántico, profundo y accesible — \
que quien lo lea sienta que el cielo los conoce mejor que ellos mismos.

REGLAS ABSOLUTAS:
• Usa SOLO los datos del JSON. Nunca inventes datos.
• Menciona ambos nombres al menos una vez en el cuerpo.
• Tono íntimo, poético, romántico — como una carta de un sabio.
• La línea ✦ debe generar anhelo sin revelar el contenido del análisis completo.
• Responde ÚNICAMENTE con el formato indicado, sin texto antes ni después.
"""


# ─────────────────────────────────────────────────────────────────────────────
# CONTEXTOS
# ─────────────────────────────────────────────────────────────────────────────

def prepare_context_individual(birth_data: dict, nombre: str) -> str:
    """Contexto para las 2 revelaciones del flujo individual."""
    today = _date.today().isoformat()
    ctx = {
        "nombre": nombre,
        "nacimiento": birth_data.get("nacimiento", {}),
        "lagna": birth_data.get("d1", {}).get("lagna", {}),
        "nakshatra_luna": birth_data.get("nakshatra_luna", {}),
        "sade_sati": birth_data.get("sade_sati", {}),
        "dasha_actual": _current_dasha(birth_data, today),
        "planeta_mas_fuerte": _strongest_planet(birth_data),
        "yogas_principales": birth_data.get("yogas", [])[:3],
        "fecha_analisis": today,
    }
    return json.dumps(ctx, ensure_ascii=False, indent=2)


def prepare_context_pareja(
    birth1: dict, nombre1: str,
    birth2: dict, nombre2: str,
) -> str:
    """Contexto para la revelación de compatibilidad (pareja)."""
    today = _date.today().isoformat()
    ctx = {
        "fecha_analisis": today,
        "persona1": {
            "nombre": nombre1,
            "nacimiento": birth1.get("nacimiento", {}),
            "lagna": birth1.get("d1", {}).get("lagna", {}),
            "nakshatra_luna": birth1.get("nakshatra_luna", {}),
            "dasha_actual": _current_dasha(birth1, today),
            "planeta_mas_fuerte": _strongest_planet(birth1),
        },
        "persona2": {
            "nombre": nombre2,
            "nacimiento": birth2.get("nacimiento", {}),
            "lagna": birth2.get("d1", {}).get("lagna", {}),
            "nakshatra_luna": birth2.get("nakshatra_luna", {}),
            "dasha_actual": _current_dasha(birth2, today),
            "planeta_mas_fuerte": _strongest_planet(birth2),
        },
    }
    return json.dumps(ctx, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS (usados también por prompts/carta.py)
# ─────────────────────────────────────────────────────────────────────────────

def _current_dasha(birth_data: dict, today: str) -> dict:
    """Encuentra el Mahadasha y Antardasha activos en la fecha de hoy."""
    mahadashas = birth_data.get("vimshottari_dasha", {}).get("mahadashas", [])

    for i, maha in enumerate(mahadashas):
        inicio = maha.get("inicio", "")
        fin = maha.get("fin", "")
        if not (inicio <= today <= fin):
            continue

        antar_actual = None
        for antar in maha.get("antardashas", []):
            if antar.get("inicio", "") <= today <= antar.get("fin", ""):
                antar_actual = {
                    "planeta": antar["planeta"],
                    "inicio": antar["inicio"],
                    "fin": antar["fin"],
                }
                break

        proximas = [
            {"planeta": m["planeta"], "inicio": m["inicio"], "fin": m["fin"]}
            for m in mahadashas[i + 1 : i + 3]
        ]

        return {
            "planeta": maha["planeta"],
            "inicio": maha["inicio"],
            "fin": maha["fin"],
            "antardasha_actual": antar_actual,
            "proximas_mahadashas": proximas,
        }

    return mahadashas[0] if mahadashas else {}


def _strongest_planet(birth_data: dict) -> dict:
    """Retorna el planeta con mayor fuerza en Shad Bala."""
    bala = birth_data.get("shad_bala", [])
    if not isinstance(bala, list) or not bala:
        return {}
    strongest = max(bala, key=lambda p: p.get("rupas", 0))
    return {
        "planeta": strongest.get("planeta", ""),
        "rupas": round(strongest.get("rupas", 0), 3),
    }


# Alias para compatibilidad con código existente (test_gancho.py)
def prepare_context(birth_data: dict, nombre: str) -> str:
    return prepare_context_individual(birth_data, nombre)

SYSTEM = SYSTEM_INDIVIDUAL
