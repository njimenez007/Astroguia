# CONTEXT.md — AstroGuía
> Documento maestro del proyecto. Leer completo antes de ejecutar cualquier tarea.
> Última actualización: Abril 25, 2026

---

## 1. ¿Qué es AstroGuía?

AstroGuía es una plataforma web de astrología védica (Jyotish) en español para el mercado hispanohablante (500M de personas). Combina los cálculos precisos de la astrología védica con inteligencia artificial entrenada en la metodología de un astrólogo védico profesional colombiano.

**Modelo de negocio:** Freemium con tres tiers.
- **Gratis:** 4 revelaciones personalizadas que generan un efecto "cómo sabías eso"
- **Pago base:** Informe completo generado automáticamente — entregado en web interactiva + descarga PDF
- **Pago premium:** Consulta personalizada 1:1 con Dario (audio o videollamada)

**Nombre:** AstroGuía
**Mercado:** Hispanohablante — prioridad Colombia y LATAM
**Stack:** Next.js + FastAPI (Python) + dashaflow + Claude Sonnet 4.6 + Wompi
**Estado actual:** Gancho gratis funcionando y validado. Construyendo informe completo.

---

## 2. El equipo

**Dario Jiménez Medina** — Astrólogo védico profesional (Jyotish). Más de 30 lecturas entregadas con feedback positivo. Creador de todo el sistema de interpretación, los prompts maestros y la metodología. Su voz y su audio son el diferenciador del producto. No toca código. AstroGuía también le sirve como herramienta interna para reemplazar su flujo manual actual con Claude Pro + Parashara's Light.

**Nicolás Jiménez** — Builder y estratega del proyecto. Maneja IA, desarrollo, producto y estrategia digital. Usa Claude, Cursor, Antigravity y vibe coding como herramientas principales. Responsable de construir y mantener todo el sistema técnico.

---

## 3. Los tres productos públicos

### Producto 1 — Carta Astral (Cita 1)
**Qué es:** Manual de identidad del consultante. Le dice quién es, cuál es su Dharma, sus fortalezas y debilidades planetarias, y en qué momento cósmico está.
**Precio:** $90.000–$120.000 COP
**Entregable:** Página web interactiva personalizada + descarga PDF elegante
**Prompt:** PLANTILLA_MAESTRA_Primera_Cita_v5 — 5 bloques secuenciales
**Estructura:**
- Bloque 1: Datos generales + personalidad + día de nacimiento
- Bloque 2: Arquetipo del Lagna + regente + elemento/cualidad
- Bloque 3: Nakshatras (Ascendente, Luna, Sol) + Doshas ayurvédicos
- Bloque 4: Shadbala (fuerza planetaria) + Jaimini Chara Karakas
- Bloque 5: 8 Pilares del Destino + Sade Sati + Mahadasha actual

---

### Producto 2 — Predicciones (Cita 2)
**Qué es:** Mapa temporal. Qué períodos planetarios está viviendo, qué viene, qué cuidar.
**Precio:** $90.000–$120.000 COP
**Entregable:** Página web interactiva personalizada + descarga PDF
**Prompt:** PROMPT_MAESTRO_JYOTISH_v4_Bloques — 4 bloques secuenciales

**Regla crítica:** Un evento solo ocurre cuando confluyen Dasha activo + Tránsito correcto + Trigger (Marte/Luna) + Ashtakavarga mayor o igual a 4 puntos + Shad Bala suficiente. Nunca predecir con un solo indicador.

---

### Producto 3 — Compatibilidad de Pareja
**Qué es:** Análisis védico de compatibilidad entre dos personas.
**Precio:** $120.000–$150.000 COP
**Entregable:** Página web interactiva personalizada + descarga PDF
**Prompt:** PLANTILLA_MAESTRA_COMPATIBILIDAD_x_Capitulos — 12 secciones

---

### Producto 4 — Consulta personalizada con Dario (Premium)
**Qué es:** El cliente quiere hablar directamente con el astrólogo.
**Opciones:** Audio personalizado (~45-60 min) o videollamada de 30 min
**Precio:** $180.000–$250.000 COP
**Flujo:** Cliente contacta a Dario directamente vía WhatsApp después de ver su informe

---

## 4. El flujo del producto público

Cliente llena datos → dashaflow calcula la carta → Claude genera 4 revelaciones gratis con streaming → Cliente ve revelaciones → CTA "Quiero mi lectura completa" → Paga con Wompi → Sistema genera informe completo automáticamente → Cliente recibe página web personalizada + PDF → Si quiere hablar con Dario → WhatsApp

Todo automático. Sin intervención humana para los productos 1, 2 y 3.

---

## 5. El Panel Admin — Herramienta interna de Dario

Panel privado que reemplaza completamente el flujo manual actual de Dario con Claude Pro + Parashara's Light.

**Funciones:**
- Ingresar datos de cliente y elegir tipo de lectura
- Generar informe completo con un clic
- Vista de lectura limpia sección por sección para preparar el audio
- Subir audio cuando esté listo

**Tiempo actual:** 1–2 horas por informe
**Tiempo con el panel:** 5–15 minutos (sin contar el audio)
**Lo que NO se automatiza:** El audio. Es el diferencial.

---

## 6. Motor de cálculos — VALIDADO ✅

**Librería:** dashaflow + pyswisseph
**Configuración:**
- Ayanamsa: Lahiri (SE_SIDM_LAHIRI)
- Sistema de casas: Whole Sign
- Nodos lunares: TRUE_NODE (confirmado por Dario en Parashara's Light)
- Coordenadas: Geocéntricas

**Validación con datos de Nicolás (28/03/2003, 08:07, Bogotá):**
- Lagna: Aries 18°01' vs Parashara 18°00' ✅
- Luna: Capricornio 25°28' Dhanishtha Pada 1 ✅
- Júpiter: Cáncer 14°13' Exaltado R ✅
- Saturno: Tauro 29°18' ✅
- Rahu: Tauro 6°14' vs Parashara 7°10' ✅ (56' diferencia aceptable — inherente al método True Node)
- Dasha Rahu 2009–2027 → Júpiter 2027 ✅
- Sade Sati 2017–2025 terminado ✅

Precisión general: menor o igual a 8 arcominutos. Aceptable para práctica Jyotish.

---

## 7. El gancho gratis — FUNCIONANDO ✅

**Orden definitivo de las 4 revelaciones:**
1. Sade Sati — fechas exactas del pasado/presente/futuro
2. Dasha activo — urgencia del momento presente
3. Yoga especial o planeta más fuerte
4. Nakshatra de la Luna — lo más íntimo

**Tono:** Gurú compasivo. Poético pero preciso. Sin tecnicismos. Se siente "ilegal" de tan específico.

**Validación:** Probado con datos reales. Feedback: "pelos de punta".

**Ajuste pendiente — Sade Sati según estado:**
- Pasado → "Los años que te forjaron tenían fecha"
- Activo → "Estás en el momento más exigente de tu vida y tiene nombre"
- Futuro → "Hay un período que viene que vas a querer conocer antes de que llegue"

---

## 8. El entregable del cliente

**Formato principal:** Página web personalizada con URL privada tipo astroguia.com/carta/nombre-id
- Diseño místico-elegante (oscuro, dorado, tipografía serif)
- Secciones navegables y colapsables
- Audio de Dario embebido (producto premium)
- Responsive — funciona en celular

**Formato secundario:** PDF descargable desde la misma página
- Diseño editorial limpio optimizado para impresión
- Generado con WeasyPrint o Puppeteer

---

## 9. Posicionamiento

**Lo que NO es:** Tarot. Predicciones del futuro. Horóscopo genérico.

**Lo que SÍ es:** Un manual de usuario de tu propia personalidad. Más cercano a un test de personalidad profundo que a una bola de cristal.

**Frase de reencuadre para escépticos:**
"Lo que estás a punto de leer no predice tu futuro. Describe quién sos, cómo funcionás, y en qué momento de tu propio ciclo vital estás. Es un manual de usuario de vos mismo — escrito en el idioma de las estrellas."

---

## 10. Stack técnico definitivo

- **Cálculos:** dashaflow + pyswisseph (local, gratis)
- **Geocoding:** timezonefinder + pytz
- **IA:** Claude Sonnet 4.6 — $0.32 USD por informe completo, $0.024 por gancho gratis
- **Fallback IA:** Gemini 2.5 Pro
- **Backend:** FastAPI — deploy en Railway ($5-7 USD/mes)
- **Frontend:** Next.js + Tailwind — deploy en Vercel (gratis)
- **Base de datos:** Firebase Firestore
- **Storage:** Firebase Storage (audios)
- **Pagos Colombia:** Wompi
- **Pagos LATAM futuro:** Mercado Pago
- **Pagos global futuro:** Stripe via LLC USA

---

## 11. Estado actual del proyecto

| Componente | Estado |
|---|---|
| Motor de cálculos (dashaflow + pyswisseph) | VALIDADO ✅ |
| Gancho gratis (4 revelaciones con streaming) | FUNCIONANDO ✅ |
| Frontend prototipo (landing + flujo freemium) | CONSTRUIDO ✅ |
| Prompts maestros (3 productos) | LISTOS ✅ |
| Ejemplos de informes reales (3 productos) | DISPONIBLES ✅ |
| API key de Claude configurada | LISTA ✅ |
| Informe completo automático | EN CONSTRUCCIÓN ⏳ |
| Vista del cliente (web interactiva) | POR CONSTRUIR ⏳ |
| Descarga PDF | POR CONSTRUIR ⏳ |
| Panel admin para Dario | POR CONSTRUIR ⏳ |
| Pasarela de pago Wompi | POR CONSTRUIR ⏳ |
| Deploy producción (Vercel + Railway) | POR CONSTRUIR ⏳ |

---

## 12. Próximos pasos en orden

1. Informe completo automático — conectar prompts de Dario con dashaflow y Claude API
2. Vista del cliente — página web personalizada con el informe
3. Descarga PDF — desde la misma página
4. Panel admin de Dario — herramienta interna
5. Cobro con Wompi
6. Deploy — Vercel + Railway
7. Ajuste Sade Sati — detectar pasado/activo/futuro
8. Optimización mobile — colapsado de texto en pantallas pequeñas

---

*AstroGuía — Jyotish AI en español · Dario Jiménez Medina + Nicolás Jiménez · Bogotá, Colombia · 2026*