"""
Prompts para la Lectura de Compatibilidad — Kundali Matching completo.
5 bloques: panorama → ascendentes → lunas → pilares → ciclos compartidos.
"""
import json
from datetime import date as _date

BLOCK_TITLES = {
    1: "La Unión en el Cosmos — Primera Vista",
    2: "Los Ascendentes — Las Dos Personalidades",
    3: "Las Lunas — La Química Emocional",
    4: "Los Pilares de la Relación",
    5: "Los Ciclos Compartidos — El Futuro de la Unión",
}

SYSTEM = """\
Eres un Astrólogo Védico Maestro especializado en Kundali Matching y compatibilidad de pareja.
Estás generando la Lectura de Compatibilidad para {nombre1} y {nombre2}.

REGLAS ABSOLUTAS:
• Usa EXCLUSIVAMENTE los datos del JSON. No inventes posiciones ni períodos.
• Tono: compasivo, honesto, esperanzador. Lenguaje para no astrólogos.
  Habla a la pareja en segunda persona del plural (ustedes, su relación).
• Equilibra: muestra las fortalezas reales Y los desafíos reales — sin endulzar ni alarmar.
• Cada bloque: mínimo 10 líneas, negritas para conceptos clave.
• Formato: Markdown. Encabezados ## y ###.
• Al terminar cada bloque: ✅ BLOQUE N COMPLETADO
"""

# ── Signos opuestos / complementarios ─────────────────────────────────────────
_SIGN_RULER = {
    "Aries": "Marte", "Tauro": "Venus", "Géminis": "Mercurio",
    "Cáncer": "Luna", "Leo": "Sol", "Virgo": "Mercurio",
    "Libra": "Venus", "Escorpio": "Marte", "Sagitario": "Júpiter",
    "Capricornio": "Saturno", "Acuario": "Saturno", "Piscis": "Júpiter",
}
_SIGN_ELEMENT = {
    "Aries": "Fuego", "Leo": "Fuego", "Sagitario": "Fuego",
    "Tauro": "Tierra", "Virgo": "Tierra", "Capricornio": "Tierra",
    "Géminis": "Aire", "Libra": "Aire", "Acuario": "Aire",
    "Cáncer": "Agua", "Escorpio": "Agua", "Piscis": "Agua",
}


def prepare_compatibilidad_context(
    birth_data1: dict, nombre1: str,
    birth_data2: dict, nombre2: str,
) -> dict:
    """Construye el contexto de compatibilidad para los dos miembros de la pareja."""

    def _chart(bd: dict, nombre: str) -> dict:
        d1 = bd.get("d1", {})
        lagna = d1.get("lagna", {})
        lagna_signo = lagna.get("signo", "")
        planets = {p["planeta"]: p for p in d1.get("planetas", [])}
        nk_luna = bd.get("nakshatra_luna", {})

        # Casa 7 (pareja axis)
        from prompts.carta import SIGNS_ORDER, SIGN_RULER
        lagna_idx = SIGNS_ORDER.index(lagna_signo) if lagna_signo in SIGNS_ORDER else 0
        casa7_signo = SIGNS_ORDER[(lagna_idx + 6) % 12]
        casa7_lord = SIGN_RULER.get(casa7_signo, "")
        casa7_lord_pos = planets.get(casa7_lord, {})
        casa7_ocupantes = [
            p["planeta"] for p in d1.get("planetas", [])
            if p.get("casa") == 7 and p["planeta"] != "Lagna"
        ]

        # Dasha actual
        from prompts.gancho import _current_dasha
        today = _date.today().isoformat()
        dasha = _current_dasha(bd, today)

        luna = planets.get("Luna", {})
        venus = planets.get("Venus", {})
        jupiter = planets.get("Júpiter", {})

        return {
            "nombre": nombre,
            "lagna": {
                "signo": lagna_signo,
                "grado": lagna.get("grado", ""),
                "elemento": _SIGN_ELEMENT.get(lagna_signo, ""),
                "regente": _SIGN_RULER.get(lagna_signo, ""),
            },
            "luna": {
                "signo": luna.get("signo", ""),
                "casa": luna.get("casa", ""),
                "dignidad": luna.get("dignidad", "—"),
            },
            "nakshatra_luna": {
                "nombre": nk_luna.get("nakshatra", bd.get("nakshatra_luna", {}).get("nombre", "")),
                "regente": nk_luna.get("regente", ""),
            },
            "venus": {
                "signo": venus.get("signo", ""),
                "casa": venus.get("casa", ""),
                "dignidad": venus.get("dignidad", "—"),
            },
            "jupiter": {
                "signo": jupiter.get("signo", ""),
                "casa": jupiter.get("casa", ""),
                "dignidad": jupiter.get("dignidad", "—"),
            },
            "casa7": {
                "signo": casa7_signo,
                "senor": casa7_lord,
                "senor_en_casa": casa7_lord_pos.get("casa", ""),
                "senor_en_signo": casa7_lord_pos.get("signo", ""),
                "ocupantes": casa7_ocupantes,
            },
            "dasha_actual": dasha,
        }

    p1 = _chart(birth_data1, nombre1)
    p2 = _chart(birth_data2, nombre2)

    return {
        "persona1": p1,
        "persona2": p2,
        "nacimiento1": birth_data1.get("nacimiento", {}),
        "nacimiento2": birth_data2.get("nacimiento", {}),
    }


def get_block_context(num: int, ctx: dict) -> dict:
    if num in [1, 2, 3, 4, 5]:
        return ctx  # Todo el contexto está disponible en todos los bloques
    return ctx


def build_block_message(num: int, block_ctx: dict) -> str:
    ctx_json = json.dumps(block_ctx, ensure_ascii=False, indent=2)
    nombre1 = block_ctx["persona1"]["nombre"]
    nombre2 = block_ctx["persona2"]["nombre"]

    if num == 1:
        return f"""BLOQUE 1 DE 5 — LA UNIÓN EN EL COSMOS

Bloque 1 de 5 para {nombre1} y {nombre2}.
Al terminar: ✅ BLOQUE 1 COMPLETADO

---

## La Unión en el Cosmos — Una Primera Vista

**1. Las Dos Cartas en Diálogo**
Presenta brevemente los Lagnas (Ascendentes) de ambas personas.
¿Qué elementos, cualidades y regentes trae cada uno a la unión?
¿Cómo se complementan o contrastan? Mínimo 6 líneas.

**2. La Primera Impresión Cósmica**
¿Cuál es la naturaleza fundamental de esta unión según los datos?
¿Es una relación de expansión, de aprendizaje, de transformación?
¿Qué tipo de vínculo describe el cosmos para estas dos cartas?
Mínimo 6 líneas.

**3. La Gran Fortaleza de Esta Unión**
¿Cuál es el punto más armonioso y poderoso de su compatibilidad?
¿Qué los une de manera profunda y duradera? Mínimo 5 líneas.

**4. El Gran Desafío de Esta Unión**
¿Cuál es el área de mayor tensión o aprendizaje que el cosmos señala?
Tono: honesto pero compasivo, orientado al crecimiento. Mínimo 5 líneas.

---
DATOS:
```json
{ctx_json}
```
"""

    if num == 2:
        return f"""BLOQUE 2 DE 5 — LOS ASCENDENTES

Bloque 2 de 5 para {nombre1} y {nombre2}. Mantén coherencia con el Bloque 1.
Al terminar: ✅ BLOQUE 2 COMPLETADO

---

## Los Ascendentes — Las Dos Personalidades en Juego

**1. El Ascendente de {nombre1}**
Analiza el Lagna de {nombre1}: su signo, elemento, regente.
¿Qué tipo de personalidad, forma de ver el mundo y estilo de vida trae?
¿Qué necesita para sentirse bien en una relación? Mínimo 6 líneas.

**2. El Ascendente de {nombre2}**
Analiza el Lagna de {nombre2}: su signo, elemento, regente.
¿Qué tipo de personalidad, forma de ver el mundo y estilo de vida trae?
¿Qué necesita para sentirse bien en una relación? Mínimo 6 líneas.

**3. El Encuentro de los dos Ascendentes**
¿Cómo interactúan estas dos formas de ser en el mundo?
¿Dónde se complementan naturalmente? ¿Dónde pueden surgir fricciones?
¿Qué roles naturales tienden a tomar en la relación? Mínimo 6 líneas.

**4. El Arte de Convivir**
¿Qué necesita entender cada uno de la forma de ser del otro?
¿Cómo pueden usar sus diferencias como fortaleza? Mínimo 5 líneas.

---
DATOS:
```json
{ctx_json}
```
"""

    if num == 3:
        return f"""BLOQUE 3 DE 5 — LAS LUNAS

Bloque 3 de 5 para {nombre1} y {nombre2}. Mantén coherencia con bloques anteriores.
Al terminar: ✅ BLOQUE 3 COMPLETADO

---

## Las Lunas — La Química Emocional

**1. La Luna de {nombre1}**
Analiza la Luna de {nombre1}: su signo, casa, nakshatra.
¿Cómo siente, qué necesita emocionalmente, cómo se nutre?
¿Cómo expresa el afecto y qué lo hace sentir seguro/a? Mínimo 6 líneas.

**2. La Luna de {nombre2}**
Analiza la Luna de {nombre2}: su signo, casa, nakshatra.
¿Cómo siente, qué necesita emocionalmente, cómo se nutre?
¿Cómo expresa el afecto y qué lo hace sentir seguro/a? Mínimo 6 líneas.

**3. La Química Emocional de la Pareja**
¿Cómo se relacionan emocionalmente sus dos Lunas?
¿Hay armonía elemental (agua-fuego, tierra-aire)?
¿Cómo se afectan mutuamente en los momentos de estrés? Mínimo 6 líneas.

**4. El Lenguaje del Amor de Esta Pareja**
¿Cómo puede cada uno nutrir mejor al otro?
¿Qué prácticas de conexión emocional sirven mejor a esta pareja?
Mínimo 5 líneas. Tono: práctico y cálido.

---
DATOS:
```json
{ctx_json}
```
"""

    if num == 4:
        return f"""BLOQUE 4 DE 5 — LOS PILARES DE LA RELACIÓN

Bloque 4 de 5 para {nombre1} y {nombre2}. Mantén coherencia con bloques anteriores.
Al terminar: ✅ BLOQUE 4 COMPLETADO

---

## Los Pilares de la Relación

**1. La Casa 7 — El Eje de la Pareja**
Para cada persona, analiza:
- El signo de la Casa 7 y su señor
- La posición del señor de Casa 7 en la carta
- ¿Qué busca cada uno en una pareja según su Casa 7?
¿Cómo se complementan o contrastan estas expectativas? Mínimo 6 líneas.

**2. Venus — El Planeta del Amor**
Analiza Venus en las dos cartas:
- Posición, signo y dignidad de cada Venus
- ¿Qué tipo de amor, romance y placer busca cada uno?
- ¿Cómo pueden satisfacer mutuamente las necesidades de Venus?
Mínimo 6 líneas.

**3. Júpiter — La Expansión y el Propósito Conjunto**
Analiza Júpiter en las dos cartas:
- ¿Cómo puede esta relación ser un vehículo de crecimiento y expansión?
- ¿Tienen un propósito de vida compatible? ¿Pueden crecer juntos?
Mínimo 5 líneas.

**4. Los Pilares Materiales — Hogar y Finanzas**
Basado en los datos disponibles, ¿qué sugiere el cosmos sobre:
- La construcción de un hogar juntos
- La compatibilidad financiera
- El estilo de vida compartido
Mínimo 5 líneas.

---
DATOS:
```json
{ctx_json}
```
"""

    if num == 5:
        return f"""BLOQUE 5 DE 5 — LOS CICLOS COMPARTIDOS

Bloque final para {nombre1} y {nombre2}. Integra todo lo analizado.
Al terminar: ✅ LECTURA DE COMPATIBILIDAD COMPLETADA

---

## Los Ciclos Compartidos — El Futuro de la Unión

**1. Los Dashas Actuales de la Pareja**
¿En qué período cósmico se encuentra cada uno hoy?
¿Cómo interactúan sus Dashas actuales? ¿Se complementan o se tensan?
¿Es este un buen momento para comprometerse, crecer juntos, o un momento de prueba?
Mínimo 6 líneas.

**2. Las Ventanas de Expansión**
Basado en los ciclos de ambos, ¿cuándo son los próximos períodos de expansión
y crecimiento para la relación? ¿Qué pueden construir juntos en esos momentos?
Mínimo 5 líneas.

**3. Los Momentos de Mayor Aprendizaje**
¿Hay períodos próximos donde la relación será puesta a prueba?
¿Qué áreas de crecimiento personal se activarán en esos momentos?
Tono: preparatorio, no alarmista. Mínimo 5 líneas.

**4. La Recomendación Cósmica para Esta Pareja**
Basado en todo el análisis, ¿cuál es la sabiduría más importante que el cosmos
ofrece para {nombre1} y {nombre2}?
¿Cuáles son las 3 prácticas o intenciones que más fortalecerían esta unión?
Mínimo 8 líneas. Sé específico y práctico.

**5. El Mensaje Final**
Una reflexión poética e inspiradora sobre esta unión.
¿Qué tiene de especial? ¿Qué promete cuando se navega con conciencia?
Cerrar con una frase poderosa y poética. Mínimo 6 líneas.

---
DATOS:
```json
{ctx_json}
```
"""

    return f"Bloque {num} no definido."
