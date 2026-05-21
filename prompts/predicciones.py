"""
Prompts para la Lectura de Predicciones — Sade Sati + Vimshottari Dasha.
5 bloques: terreno actual → mahadasha → antardasha → mapa próximos 24 meses → estrategia.
"""
import json
from datetime import date as _date, datetime as _dt
from typing import Any

BLOCK_TITLES = {
    1: "El Ciclo de Saturno — Tu Terreno Actual",
    2: "El Gran Período — Tu Mahadasha",
    3: "El Momento Interno — Tu Antardasha",
    4: "El Mapa de los Próximos 24 Meses",
    5: "Tu Brújula Cósmica — Estrategia e Integración",
}

SYSTEM = """\
Eres un Astrólogo Védico Maestro especializado en Jyotish predictivo — ciclos de tiempo, Dashas y Sade Sati.
Estás generando la Lectura de Predicciones para {nombre}.

REGLAS ABSOLUTAS:
• Usa EXCLUSIVAMENTE los datos del JSON. No inventes fechas ni períodos.
• Tono: Gurú compasivo. Lenguaje para no astrólogos — sin tecnicismos sin traducir.
  Registro: Maestro — Guía — Estratega Cósmico.
• Cada bloque debe sentirse como una revelación práctica, no solo descripción.
• Mínimo 10 líneas por bloque. Negritas para conceptos clave.
• Formato: Markdown. Encabezados ## y ###. Negritas, listas.
• Al terminar cada bloque: ✅ BLOQUE N COMPLETADO
"""


def prepare_predicciones_context(birth_data: dict, nombre: str) -> dict:
    """Construye el contexto relevante para la lectura de predicciones."""
    today = _date.today().isoformat()
    dasha_data = birth_data.get("vimshottari_dasha", {})
    sade_sati = birth_data.get("sade_sati", {})
    nac = birth_data.get("nacimiento", {})

    # ── Mahadasha actual ──────────────────────────────────────────────────────
    current_maha: dict = {}
    current_antar: dict = {}
    upcoming_antars: list = []
    upcoming_mahas: list = []

    mahas = dasha_data.get("mahadashas", [])
    for i, maha in enumerate(mahas):
        if maha["inicio"] <= today <= maha["fin"]:
            current_maha = maha
            # Antardasha actual
            for j, antar in enumerate(maha.get("antardashas", [])):
                if antar["inicio"] <= today <= antar["fin"]:
                    current_antar = antar
                    upcoming_antars = maha["antardashas"][j + 1: j + 4]
                    break
            # Próximas mahadashas
            upcoming_mahas = [
                {"planeta": m["planeta"], "inicio": m["inicio"], "fin": m["fin"]}
                for m in mahas[i + 1: i + 3]
            ]
            break

    # ── Planetas clave ────────────────────────────────────────────────────────
    d1_planets = {p["planeta"]: p for p in birth_data.get("d1", {}).get("planetas", [])}
    planetas_clave = {
        name: {
            "signo": d1_planets[name].get("signo", ""),
            "casa": d1_planets[name].get("casa", ""),
            "dignidad": d1_planets[name].get("dignidad", "—"),
        }
        for name in ["Saturno", "Júpiter", "Rahu", "Ketu", "Luna"]
        if name in d1_planets
    }

    return {
        "nombre": nombre,
        "hoy": today,
        "nacimiento": {"fecha": nac.get("fecha", ""), "ciudad": nac.get("ciudad", "")},
        "sade_sati": sade_sati,
        "mahadasha_actual": {
            "planeta": current_maha.get("planeta", ""),
            "inicio": current_maha.get("inicio", ""),
            "fin": current_maha.get("fin", ""),
        },
        "antardasha_actual": {
            "planeta": current_antar.get("planeta", ""),
            "inicio": current_antar.get("inicio", ""),
            "fin": current_antar.get("fin", ""),
        },
        "proximas_antardashas": [
            {"planeta": a["planeta"], "inicio": a["inicio"], "fin": a["fin"]}
            for a in upcoming_antars
        ],
        "proximas_mahadashas": upcoming_mahas,
        "planetas_clave": planetas_clave,
    }


def get_block_context(num: int, ctx: dict) -> dict:
    base = {"nombre": ctx["nombre"], "hoy": ctx["hoy"], "nacimiento": ctx["nacimiento"]}
    if num == 1:
        return {**base, "sade_sati": ctx["sade_sati"], "planetas_clave": {"Saturno": ctx["planetas_clave"].get("Saturno", {})}}
    if num == 2:
        return {**base,
                "mahadasha_actual": ctx["mahadasha_actual"],
                "proximas_mahadashas": ctx["proximas_mahadashas"],
                "planetas_clave": ctx["planetas_clave"]}
    if num == 3:
        return {**base,
                "mahadasha_actual": ctx["mahadasha_actual"],
                "antardasha_actual": ctx["antardasha_actual"],
                "planetas_clave": ctx["planetas_clave"]}
    if num == 4:
        return {**base,
                "antardasha_actual": ctx["antardasha_actual"],
                "proximas_antardashas": ctx["proximas_antardashas"],
                "proximas_mahadashas": ctx["proximas_mahadashas"]}
    if num == 5:
        return ctx  # Todo el contexto para la síntesis
    return ctx


def build_block_message(num: int, block_ctx: dict) -> str:
    ctx_json = json.dumps(block_ctx, ensure_ascii=False, indent=2)
    nombre = block_ctx["nombre"]

    if num == 1:
        return f"""BLOQUE 1 DE 5 — EL CICLO DE SATURNO

Estás generando el Bloque 1 de 5 para {nombre}.
Al terminar: ✅ BLOQUE 1 COMPLETADO

---

## El Ciclo de Saturno — El Terreno que Pisas Hoy

Analiza el Sade Sati de {nombre} usando los datos del JSON.

**1. Estado Actual del Ciclo de Saturno**
Usa "sade_sati.activo_hoy" y "sade_sati.fase_actual" del JSON.
- ¿Está en Sade Sati activo o en estado de libertad?
- Si activo: ¿en qué fase? (ascendente / pico / descendente) — mínimo 4 líneas
- Si inactivo: ¿cuándo terminó? ¿qué significa este estado de LIBERTAD? — mínimo 4 líneas

**2. Los Ciclos de Saturno — El Mapa Histórico**
Usando los ciclos del JSON, describe el patrón de prueba-libertad en la vida de {nombre}.
¿Cuándo vivió o vivirá los períodos más intensos? Mínimo 5 líneas.

**3. Lo que Saturno Enseñó (o Está Enseñando)**
¿Qué lecciones fundamentales de madurez, responsabilidad y estructura está
trabajando {nombre}? Conecta con la posición de Saturno en el JSON.
Tono: compasivo, motivador, sin fatalismo. Mínimo 6 líneas.

**4. El Terreno de Hoy**
¿Qué tipo de terreno está pisando {nombre} en este momento según el ciclo de Saturno?
¿Qué tipo de energía tiene disponible? ¿Qué le conviene hacer y qué evitar?
Mínimo 5 líneas.

---
DATOS:
```json
{ctx_json}
```
"""

    if num == 2:
        return f"""BLOQUE 2 DE 5 — EL GRAN PERÍODO (MAHADASHA)

Bloque 2 de 5 para {nombre}. Mantén coherencia con el Bloque 1.
Al terminar: ✅ BLOQUE 2 COMPLETADO

---

## El Gran Período — La Era que Gobierna Tu Vida

Analiza el Mahadasha actual de {nombre} usando los datos del JSON.

**1. El Planeta que Rige Esta Era**
¿Cuál es el planeta del Mahadasha actual? ¿Cuánto tiempo dura?
¿Cuándo empezó? ¿Cuándo termina?
Explica la naturaleza y esencia de este planeta — qué rige, qué impulsa, qué trae.
Mínimo 6 líneas.

**2. Los Dones de Esta Era para {nombre}**
¿Qué oportunidades, fortalezas y aperturas trae este período?
¿En qué áreas de vida (trabajo, finanzas, relaciones, espiritualidad) se activa?
Usa la posición del planeta en el JSON para hacer la interpretación específica.
Mínimo 6 líneas.

**3. Las Pruebas y Tensiones de Esta Era**
¿Qué desafíos o áreas de crecimiento exige este Mahadasha?
¿Qué tendencias de sombra pueden activarse? Tono: motivador, no fatalista.
Mínimo 5 líneas.

**4. El Próximo Gran Período — La Visión Futura**
Usando proximas_mahadashas del JSON, describe brevemente qué se aproxima
después de este Mahadasha. ¿Cómo prepararse para esa transición?
Mínimo 5 líneas.

---
DATOS:
```json
{ctx_json}
```
"""

    if num == 3:
        return f"""BLOQUE 3 DE 5 — EL MOMENTO INTERNO (ANTARDASHA)

Bloque 3 de 5 para {nombre}. Mantén coherencia con bloques anteriores.
Al terminar: ✅ BLOQUE 3 COMPLETADO

---

## El Momento Interno — El Sub-Período que Colorea el Presente

Analiza el Antardasha actual de {nombre} usando los datos del JSON.

**1. El Planeta del Momento**
¿Qué planeta rige el Antardasha actual? ¿Cuándo empezó y termina?
¿Cómo dialoga este sub-regente con el Mahadasha principal?
Describe la dinámica entre los dos planetas (concordancia o tensión).
Mínimo 6 líneas.

**2. Lo que Activa Este Momento**
¿Qué áreas específicas de la vida se iluminan en este Antardasha?
¿Qué proyectos, relaciones o áreas merecen atención especial ahora?
Usa la posición del planeta en el JSON. Mínimo 6 líneas.

**3. El Foco Óptimo para Este Período**
¿En qué debería concentrarse {nombre} en este Antardasha?
¿Qué puede lograr con mayor facilidad? ¿Qué debe evitar o posponer?
Mínimo 5 líneas. Tono: práctico y motivador.

**4. La Duración y el Ritmo**
¿Cuándo termina este Antardasha? ¿Qué viene inmediatamente después?
¿Cómo prepararse para esa transición? Mínimo 4 líneas.

---
DATOS:
```json
{ctx_json}
```
"""

    if num == 4:
        return f"""BLOQUE 4 DE 5 — EL MAPA DE LOS PRÓXIMOS 24 MESES

Bloque 4 de 5 para {nombre}. Mantén coherencia con bloques anteriores.
Al terminar: ✅ BLOQUE 4 COMPLETADO

---

## El Mapa de los Próximos 24 Meses

Usando proximas_antardashas del JSON, construye un mapa temporal concreto.

**1. Las Próximas Puertas que se Abren**
Para cada Antardasha próximo en el JSON, describe:
- El planeta, período exacto (inicio → fin)
- El tipo de energía que trae
- Las oportunidades que abre
- Las áreas de vida que activa
Mínimo 4 líneas por período.

**2. Las Ventanas de Oro**
¿Cuáles de los próximos períodos son especialmente favorables?
¿Para qué acciones concretas (iniciar proyectos, inversiones, relaciones, estudios)?
Sé específico con fechas aproximadas. Mínimo 5 líneas.

**3. Los Momentos de Introspección**
¿Hay períodos en los próximos 24 meses que pidan más cuidado o reflexión?
¿Qué tipo de enfoque se recomienda durante esas fases?
Tono: preparatorio, no alarmista. Mínimo 4 líneas.

**4. La Transición del Mahadasha (si aplica)**
Si el Mahadasha cambia en los próximos 24 meses, explica esta transición mayor.
¿Qué significará para {nombre} ese cambio de era?

---
DATOS:
```json
{ctx_json}
```
"""

    if num == 5:
        return f"""BLOQUE 5 DE 5 — TU BRÚJULA CÓSMICA (SÍNTESIS Y ESTRATEGIA)

Bloque final para {nombre}. Integra los 4 bloques anteriores.
Al terminar: ✅ LECTURA DE PREDICCIONES COMPLETADA

---

## Tu Brújula Cósmica — Estrategia e Integración

**1. La Fotografía Completa de Tu Momento**
Sintetiza el estado actual: ciclo de Saturno + Mahadasha + Antardasha.
¿Qué tipo de momento vive {nombre}? ¿Cómo se llaman estos vientos?
Mínimo 6 líneas.

**2. Las Tres Prioridades del Período**
Basado en todos los ciclos analizados, ¿cuáles son las 3 áreas de vida que
merecen mayor atención y energía en este momento?
Para cada una: qué hacer, por qué ahora, qué resultado esperar. Mínimo 8 líneas.

**3. Las Tres Cosas que NO Hacer**
¿Qué tipo de acciones, decisiones o patrones no van con la energía de este período?
¿Qué conviene posponer o evitar? Tono: práctico, no prohibitivo. Mínimo 5 líneas.

**4. Remedios Védicos para Este Período**
Basado en los planetas activos (Mahadasha y Antardasha), sugiere prácticas védicas:
- Mantras específicos o afirmaciones
- Colores, alimentos, días de la semana favorables
- Tipo de servicio o acción kármica recomendada
- Práctica espiritual que sintoniza con este período
Mínimo 6 líneas.

**5. El Mensaje Final del Cosmos para {nombre}**
Una reflexión poética e inspiradora que integre todo el análisis.
¿Cuál es la promesa de este período? ¿Qué viene cuando se navega bien?
Mínimo 6 líneas. Cerrar con una frase poderosa.

---
DATOS:
```json
{ctx_json}
```
"""

    return f"Bloque {num} no definido."
