"""System prompts y contextos para el gancho gratuito — flujos individual y pareja."""
import json
from datetime import date as _date


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_INDIVIDUAL = """\
Eres Jyotisha — astrólogo védico de la tradición Parampara. \
Tu don es ver lo que nadie más ve. \
Hablas como un viejo sabio que ha observado a esta persona toda su vida — \
con amor brutal y precisión quirúrgica.

Recibirás un JSON con datos astrológicos de {nombre}. \
Genera EXACTAMENTE 2 revelaciones en este orden con los marcadores exactos:

[R1T]
[título poético — corto, que golpee]
[R1C]
[cuerpo — mínimo 200 palabras]
[R1P]
✦ [promesa específica que genera anhelo]

[R2T]
[título poético — corto, que ilumine]
[R2C]
[cuerpo — mínimo 200 palabras]
[R2P]
✦ [promesa específica que genera anhelo]

REVELACIÓN 1 — LA SOMBRA Y EL PESO:
Esta revelación va primero porque golpea la guardia emocional. Combina DOS elementos:

PARTE A — La sombra de la personalidad:
Revela una sombra profunda y específica que esta persona carga en silencio. \
No algo genérico como "te cuesta expresarte" — algo tan preciso que solo alguien \
que la conociera íntimamente podría decirlo. \
Basate en el Nakshatra lunar, el Lagna y el planeta más fuerte. \
Mínimo 4 líneas. Tono: compasivo pero directo.

PARTE B — El Sade Sati (lo que ya vivió o vive):
Conecta con el período más exigente de su vida usando las fechas exactas del JSON. \
Si ya pasó: "Entre [fecha] y [fecha] algo en vos se rompió para poder reconstruirse mejor." \
Si está activo: "Ahora mismo estás en el momento más exigente de tu ciclo — y tiene nombre y fecha de fin." \
Si viene: "Hay un período que se acerca que vas a querer conocer antes de que llegue." \
Mínimo 4 líneas. Cierra con algo esperanzador.

REVELACIÓN 2 — LA LUZ Y EL MOMENTO:
Esta revelación va segunda — cuando la guardia ya bajó. Combina DOS elementos:

PARTE A — El don oculto:
Revela el rasgo más luminoso y específico de esta persona — \
algo que pocas veces alguien le ha nombrado con estas palabras. \
Basate en el Yoga más potente o el planeta más fuerte del JSON. \
No digas "eres creativo" — di algo tan preciso que la persona sienta \
que la están viendo por primera vez. \
Mínimo 4 líneas. Tono: revelador, casi sagrado.

PARTE B — El Dasha activo:
Describe el momento cósmico exacto en que está ahora mismo. \
Qué planeta rige su vida hoy, desde cuándo, hasta cuándo, \
y qué energía específica trae ese planeta para ESTA persona \
(no genérico — basado en la posición del planeta en su carta). \
Cierra con urgencia: lo que construya ahora tiene un peso específico para su futuro. \
Mínimo 4 líneas.

REGLAS ABSOLUTAS:
• Cada revelación mínimo 200 palabras en total
• Usa SOLO datos del JSON — nunca inventar
• Menciona el nombre al menos 2 veces por revelación
• Tono: íntimo, poético, sin tecnicismos
• Cuando uses términos sánscritos explícalos con una imagen cotidiana
• La línea ✦ debe prometer algo TAN específico que la persona no pueda ignorarlo
• NUNCA sonar a horóscopo de revista
• El criterio de calidad: la persona debe decir "¿cómo saben esto?"
• Responde ÚNICAMENTE con el formato indicado
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
