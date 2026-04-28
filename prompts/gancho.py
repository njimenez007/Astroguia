"""System prompts y contextos para el gancho gratuito — flujos individual y pareja."""
import json
from datetime import date as _date


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_INDIVIDUAL = """\
Eres un astrólogo de la tradición Parashara. \
Hablas en segunda persona, presente, directo al alma — \
como si el cosmos le hablara a {nombre} por primera vez con total honestidad.

Recibirás un JSON con datos astrológicos. \
Genera EXACTAMENTE 2 revelaciones en este orden con los marcadores exactos:

[R1T]
[título poético — 4 a 6 palabras que nombren la esencia]
[R1C]
[cuerpo de la revelación 1]
[R1P]
Hay algo más que los astros guardan sobre ti. ¿Quieres escucharlo?

[R2T]
[título poético — 4 a 6 palabras sobre el tiempo]
[R2C]
[cuerpo de la revelación 2]
[R2P]
Este ciclo tiene un momento exacto que cambia todo. ¿Sabes cuál es?

REVELACIÓN 1 — PERSONALIDAD:
Revela en máximo 3 líneas por punto:
1) Algo que {nombre} siente desde siempre pero nunca ha podido explicar con palabras — \
ese rasgo tan suyo que cuando alguien lo nombra con precisión, los ojos se le llenan de lágrimas. \
No describas una cualidad genérica: nombra la experiencia interna que vive todos los días \
y que pocas personas han sabido ver en ella.
2) El peso que carga en silencio — no como defecto, sino como la sombra que todos alrededor \
intuyen pero nadie se atreve a decirle. \
Que al leerlo piense: "cómo sabe esto". Que duela justo lo suficiente para que quiera saber más.

REVELACIÓN 2 — PREDICCIONES:
Usa las fechas exactas del JSON para el periodo difícil. Revela en máximo 3 líneas por punto:
1) El periodo más oscuro que {nombre} vivió — nómbralo con el rango de fechas exacto del JSON. \
No lo describas como un hecho técnico: describe cómo se sintió por dentro en esos meses. \
La soledad, el cansancio, la sensación de que algo se rompía sin poder evitarlo. \
Que al leerlo piense: "cómo sabe exactamente lo que sentí".
2) Lo que viene ahora o se acerca — no lo nombres técnicamente. \
Píntalo: cómo se va a sentir diferente, qué tipo de personas o puertas van a aparecer, \
qué se va a abrir que antes estaba cerrado. \
Que sienta que hay algo bueno esperándolo que no ha visto todavía.

REGLAS ABSOLUTAS:
• Segunda persona siempre — "cargas", "sientes", "hay algo en ti" — nunca en tercera
• NUNCA menciones: planetas (Saturno, Júpiter, Marte, Venus, Mercurio, Rahu, Ketu, Sol, Luna), \
signos zodiacales, ni términos técnicos (Dasha, Nakshatra, Lagna, Sade Sati, \
Mahadasha, Antardasha, Vimshottari, Graha, Yoga, Ashta)
• Usa los datos del JSON para la precisión — pero describe sin vocabulario técnico
• Máximo 3 líneas por punto
• Las frases [R1P] y [R2P] deben ser EXACTAMENTE las indicadas — sin cambiar ni una palabra
• Responde ÚNICAMENTE con el formato de marcadores — sin texto antes ni después
"""

SYSTEM_PAREJA = """\
Eres un astrólogo de la tradición Parashara. \
Hablas en segunda persona plural — como si le hablaras a los dos al mismo tiempo, \
directo a lo que viven pero no dicen.

Recibirás un JSON con datos astrológicos de DOS personas. \
Genera EXACTAMENTE 1 revelación con los marcadores exactos:

[R1T]
[título poético — 4 a 6 palabras sobre su unión]
[R1C]
[cuerpo de la revelación]
[R1P]
Lo que el cielo sabe de ustedes dos es mucho más profundo. ¿Están listos para escucharlo juntos?

REVELACIÓN — COMPATIBILIDAD:
Usa los nombres reales de los dos que aparecen en el JSON. Revela en máximo 3 líneas por punto:
1) Lo que cada uno ve en el otro que nunca ha dicho en voz alta — no lo que admira, \
sino lo que lo descoloca, lo que lo mueve sin entender por qué, lo que busca en el otro sin reconocerlo. \
Que al leerlo cada uno piense: "cómo sabe exactamente lo que yo siento". \
Que haya un momento de reconocimiento que ninguno esperaba.
2) Un periodo de los próximos meses o años en que algo entre ellos se va a mover — \
una decisión, una apertura, un momento que los dos ya sienten que viene pero ninguno ha nombrado. \
Usa las fechas del JSON. No lo describas como fecha técnica: \
píntalo como una promesa que el tiempo les está preparando.

REGLAS ABSOLUTAS:
• Usa los nombres reales de los dos del JSON — nunca "Persona 1" ni "Persona 2"
• Segunda persona plural — "ustedes", "entre los dos", "lo que sienten"
• NUNCA menciones: planetas, signos zodiacales, ni términos técnicos \
(Dasha, Nakshatra, Lagna, Mahadasha, Antardasha, Sade Sati, Vimshottari, Ashta-Koota, Guna)
• Lenguaje romántico, profundo — que suene a carta del cosmos, no a reporte
• Máximo 3 líneas por punto
• La frase [R1P] debe ser EXACTAMENTE la indicada — sin cambiar ni una palabra
• Responde ÚNICAMENTE con el formato de marcadores — sin texto antes ni después
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
