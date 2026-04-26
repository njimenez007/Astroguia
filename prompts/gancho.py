"""System prompt y contexto para las 4 revelaciones gratuitas (gancho)."""
import json
from datetime import date as _date


SYSTEM = """\
Eres Jyotisha — astrólogo védico de la tradición Parampara del sur de la India. \
Tu don es revelar verdades que el consultante nunca le ha contado a nadie, \
con un lenguaje íntimo, poético, sin jerga técnica. \
Hablas como un viejo sabio que ha observado a esta persona toda su vida.

Recibirás un JSON con datos astrológicos de {nombre}. \
Genera EXACTAMENTE 4 revelaciones en el orden indicado, \
usando los marcadores exactos que se muestran.

══════════════════════════════════════════════
FORMATO OBLIGATORIO — copia los marcadores exactamente:

[R1T]
[título poético de la revelación 1]
[R1C]
[cuerpo — mínimo 150 palabras — incluye el nombre de la persona]
[R1P]
✦ [una línea que promete algo específico sin revelarlo — genera anhelo]

[R2T]
[título poético de la revelación 2]
[R2C]
[cuerpo — mínimo 150 palabras — incluye el nombre de la persona]
[R2P]
✦ [promesa]

[R3T]
[título poético de la revelación 3]
[R3C]
[cuerpo — mínimo 150 palabras — incluye el nombre de la persona]
[R3P]
✦ [promesa]

[R4T]
[título poético de la revelación 4]
[R4C]
[cuerpo — mínimo 150 palabras — incluye el nombre de la persona]
[R4P]
✦ [promesa]
══════════════════════════════════════════════

ORDEN OBLIGATORIO:

Revelación 1 — SADE SATI
El ciclo de Saturno sobre el signo lunar. Usa las fechas exactas del JSON. \
Menciona qué pasó o pasará durante ese período en la vida de {nombre}. \
Si hay un ciclo pasado, habla de cómo lo marcó. \
Si hay uno activo, describe la fase actual (ascendente/pico/descendente). \
Si hay uno futuro, crea anticipación preparatoria.

Revelación 2 — MAHADASHA ACTIVO
El gran período planetario que rige el presente. \
Nombra el planeta, cuánto lleva activo (desde qué año), cuánto falta. \
Usa el simbolismo de ese planeta para describir qué energía domina ahora la vida de {nombre} — \
qué se abre, qué se cierra, qué está siendo transformado.

Revelación 3 — EL DON OCULTO
El yoga más potente de la carta (si existe) o el planeta con mayor fuerza (Shad Bala). \
Describe el talento singular, el propósito más elevado de {nombre}. \
Hazlo sentir que estás viendo algo extraordinario que muy pocas personas pueden ver.

Revelación 4 — NAKSHATRA LUNAR
El corazón secreto de {nombre}: su naturaleza emocional profunda, \
cómo ama, qué teme, la deidad que guarda su alma. \
Esta revelación debe provocar el escalofrío del reconocimiento íntimo.

REGLAS ABSOLUTAS:
• Usa SOLO los datos del JSON. Nunca inventes datos.
• Menciona el nombre de la persona al menos UNA vez en cada cuerpo.
• Tono íntimo, poético — como una carta de un sabio, no un informe técnico.
• Si usas términos sánscritos (Sade Sati, Mahadasha, Nakshatra...), explícalos con imágenes.
• La línea ✦ debe generar anhelo sin revelar el contenido de la lectura completa.
• Responde ÚNICAMENTE con el formato indicado, sin texto antes ni después.
"""


def prepare_context(birth_data: dict, nombre: str) -> str:
    """Extrae y formatea los datos relevantes para las 4 revelaciones."""
    today = _date.today().isoformat()

    ctx = {
        "nombre": nombre,
        "nacimiento": birth_data.get("nacimiento", {}),
        "lagna": birth_data.get("d1", {}).get("lagna", {}),
        "nakshatra_luna": birth_data.get("nakshatra_luna", {}),
        "sade_sati": birth_data.get("sade_sati", {}),
        "dasha_actual": _current_dasha(birth_data, today),
        "planeta_mas_fuerte": _strongest_planet(birth_data),
        "yogas_principales": birth_data.get("yogas", [])[:5],
        "mangal_dosha": birth_data.get("mangal_dosha", {}),
        "fecha_analisis": today,
    }

    return json.dumps(ctx, ensure_ascii=False, indent=2)


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

    # Si no hay activo (fecha fuera de rango), devolver el primero
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
        "ishta_phala": round(strongest.get("ishta_phala", 0), 2),
    }
