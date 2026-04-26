import { NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

export const dynamic = 'force-dynamic'
export const maxDuration = 60

// ─── Constants ────────────────────────────────────────────────────────────────
const PROKERALA_BASE = 'https://api.prokerala.com'
const OPENCAGE_URL = 'https://api.opencagedata.com/geocode/v1/json'
const AYANAMSA = 1 // Lahiri (Chitra Paksha) — mismo que Parashara's Light

// ─── Types ────────────────────────────────────────────────────────────────────
interface GeoResult {
  lat: number
  lon: number
  timezone: string
  offsetSec: number
}

export interface Revelaciones {
  lagna: string
  nakshatra_luna: string
  mahadasha: string
  saturno: string
}

// ─── Mock mode ───────────────────────────────────────────────────────────────
// Activar con MOCK_MODE=true en .env.local

interface MockProfile {
  lagna: string; lagnaGrado: number; nakshatra: string; rashi: string
  dashaPlaneta: string; dashaInicio: string; dashaFin: string
  antarDasha: string; antarFin: string
  saturnSigno: string; saturnCasa: string; sadeSati: boolean
}

const MOCK_PROFILES: MockProfile[] = [
  {
    lagna: 'Aries', lagnaGrado: 14, nakshatra: 'Rohini', rashi: 'Tauro',
    dashaPlaneta: 'Júpiter', dashaInicio: '2020', dashaFin: '2036',
    antarDasha: 'Saturno', antarFin: '2026',
    saturnSigno: 'Acuario', saturnCasa: '11', sadeSati: false,
  },
  {
    lagna: 'Virgo', lagnaGrado: 22, nakshatra: 'Jyeshtha', rashi: 'Escorpio',
    dashaPlaneta: 'Venus', dashaInicio: '2019', dashaFin: '2039',
    antarDasha: 'Sol', antarFin: '2025',
    saturnSigno: 'Piscis', saturnCasa: '7', sadeSati: true,
  },
  {
    lagna: 'Sagitario', lagnaGrado: 8, nakshatra: 'Purva Bhadrapada', rashi: 'Acuario',
    dashaPlaneta: 'Saturno', dashaInicio: '2021', dashaFin: '2040',
    antarDasha: 'Venus', antarFin: '2027',
    saturnSigno: 'Capricornio', saturnCasa: '2', sadeSati: false,
  },
  {
    lagna: 'Escorpio', lagnaGrado: 3, nakshatra: 'Chitra', rashi: 'Virgo',
    dashaPlaneta: 'Mercurio', dashaInicio: '2018', dashaFin: '2035',
    antarDasha: 'Ketu', antarFin: '2025',
    saturnSigno: 'Libra', saturnCasa: '12', sadeSati: false,
  },
]

function buildMockRevelaciones(nombre: string, p: MockProfile): Revelaciones {
  const n = nombre.split(' ')[0] // primer nombre para más naturalidad

  const lagna = `${n}, tu Lagna en ${p.lagna} a ${p.lagnaGrado}° es la primera frase que el cosmos pronunció sobre ti en el instante exacto en que llegaste a este mundo. ${p.lagna} no es solo un signo: es el arquetipo que define cómo percibes la realidad, cómo atraes a las personas y de qué manera construyes tu camino con tus propias manos. Lo que muchos no ven en ti desde afuera, tu Lagna lo explica con una precisión que puede sorprender: hay una forma de ser tuya —un tono, una energía— que es reconocible antes de que digas una sola palabra. El reto y el regalo de este Ascendente viven en la misma moneda: aprender a usar esa fuerza con consciencia en lugar de dejarla correr sin dirección. ${nombre}, cuando comprendes plenamente el lenguaje de tu Lagna, dejas de pelear contra tu naturaleza y empiezas a colaborar con ella. Como dice la tradición Jyotish: el Lagna es la semilla; todo lo que llegarás a ser ya está inscrito en ese primer grado del cielo.`

  const nakshatra_luna = `${n}, tu Luna habita en ${p.nakshatra}, en el signo de ${p.rashi} — y esta combinación revela algo sobre ti que pocos ven a primera vista. ${p.nakshatra} es uno de los Nakshatras más profundos del zodiaco védico: tiene una energía que oscila entre la intensidad y la sabiduría, entre el dolor y el poder que nace de haber atravesado ese dolor. Tu mundo emocional interno —el lugar donde vives cuando nadie te mira— está gobernado por este Nakshatra, lo que significa que procesas las experiencias de una manera que puede resultar incomprensible para las personas más superficiales. No te asombra la complejidad: te atrae. Lo que más sorprende a quienes te conocen bien es tu capacidad de sentir profundo sin derrumbarte, de atravesar tormentas internas con una calma exterior que parece contradecir lo que realmente ocurre dentro. ${nombre}, esto no es frialdad — es la fortaleza particular de quien tiene la Luna donde tú la tienes. La luna en ${p.nakshatra} no nació para aguas tranquilas; nació para navegar lo que otros no se atreven a cruzar.`

  const mahadasha = `${nombre}, el planeta que rige tu vida en este momento preciso es ${p.dashaPlaneta}, cuyo Mahadasha comenzó alrededor de ${p.dashaInicio} y se extenderá hasta ${p.dashaFin}. Esto no es un detalle menor en tu carta: el Mahadasha es el gran director de escena de tu vida, el que determina qué temas cobran protagonismo, qué puertas se abren y cuáles permanecen cerradas durante un período largo. Si observas tu vida desde ${p.dashaInicio} hacia acá, es muy probable que identifiques un patrón claro: algo relacionado con la energía de ${p.dashaPlaneta} se volvió central —ya sea un tipo de relación, un tipo de trabajo, un proceso interno que no puedes ignorar. El Antardasha actual es de ${p.antarDasha}, lo que crea una combinación específica dentro del período mayor: ${p.dashaInicio} y ${p.antarFin} es una ventana de tensión creativa donde el planeta principal y el subperíodo trabajan en direcciones que se complementan si sabes usarlas. ${nombre}, lo que estás construyendo en esta ventana tiene raíces más profundas de lo que parece. 'El Mahadasha no te da lo que pides — te da lo que necesitas para convertirte en quien debes ser.'`

  const saturno = p.sadeSati
    ? `${nombre}, Saturno está transitando sobre tu Luna en ${p.rashi} — lo que en la tradición védica se conoce como Sade Sati, el período de siete años y medio que el gran maestro del sistema solar dedica a revisarte por completo. No te voy a mentir: el Sade Sati es exigente. Puede sentirse como que el mundo te pone resistencia en todos los frentes al mismo tiempo — el trabajo, las relaciones, la salud, la identidad misma. Pero hay algo que la mayoría no dice sobre este período: el Sade Sati no destruye lo que es genuino; purifica lo que no era real. Lo que estás perdiendo ahora —si es que estás perdiendo algo— es lo que necesitaba irse para que lo verdadero ocupe su lugar. Saturno en ${p.saturnSigno}, Casa ${p.saturnCasa} de tu carta, trabaja con una lógica de largo plazo que puede ser frustrante en el corto. ${nombre}, quienes salen del Sade Sati con consciencia —en lugar de salir agotados— emergen con una claridad sobre sí mismos que no existía antes. Esta presión no es castigo: es escultura. 'El diamante solo nace bajo presión extrema — y Saturno lo sabe.'`
    : `${nombre}, Saturno habita en ${p.saturnSigno} en la Casa ${p.saturnCasa} de tu carta natal, y en este momento NO está en fase de Sade Sati — lo que significa que no estás en el período de presión directa sobre tu Luna. Esta es una noticia importante: cualquier dificultad que estés viviendo ahora no viene del gran maestro en su modo más exigente, sino de otras dinámicas de tu carta que tienen soluciones más accesibles. La posición de Saturno en tu Casa ${p.saturnCasa} habla de un área específica de tu vida donde el cosmos te pide madurez y estructura en lugar de velocidad. Saturno en ${p.saturnSigno} trabaja lentamente pero con una solidez que pocas otras energías planetarias pueden igualar: lo que construyes bajo su influencia —con paciencia, con rigor— tiende a durar décadas. ${nombre}, el período de presión saturnina intensa que quizás viviste hace unos años ya pasó o aún está por llegar — hoy tienes una ventana de mayor fluidez que deberías aprovechar. 'Saturno no quita — afina. Y lo que afina en ti, ${nombre}, es el diamante.'`

  return { lagna, nakshatra_luna, mahadasha, saturno }
}

async function getMockResponse(nombre: string, fecha: string) {
  // Pequeño delay para que el loading screen se pueda apreciar
  await new Promise((r) => setTimeout(r, 4000))

  const [year, month, day] = fecha.split('-').map(Number)
  const seed = (year % 100) + month * 7 + day * 3
  const profile = MOCK_PROFILES[seed % MOCK_PROFILES.length]

  return {
    birth_data: {
      nombre, fecha, ciudad: '(simulación)',
      moon_nakshatra: { name: profile.nakshatra },
      moon_rashi: { name: profile.rashi },
      ascendant: { name: 'Ascendant', rashi: { name: profile.lagna }, longitude: profile.lagnaGrado },
      saturn: { name: 'Saturn', rashi: { name: profile.saturnSigno }, house: parseInt(profile.saturnCasa) },
      dasha_periods: { planet: profile.dashaPlaneta, start_date: profile.dashaInicio, end_date: profile.dashaFin },
    },
    revelaciones: buildMockRevelaciones(nombre, profile),
    datetime: `${fecha}T00:00:00-05:00`,
    mock: true,
  }
}

// ─── Geocoding ────────────────────────────────────────────────────────────────
async function geocode(ciudad: string): Promise<GeoResult> {
  const url = `${OPENCAGE_URL}?q=${encodeURIComponent(ciudad)}&key=${process.env.OPENCAGE_API_KEY}&limit=1&language=es&no_annotations=0`
  const resp = await fetch(url)
  if (!resp.ok) throw new Error('Error al geocodificar la ciudad')
  const data = await resp.json()
  const results: unknown[] = data.results ?? []
  if (results.length === 0) throw new Error(`Ciudad no encontrada: "${ciudad}"`)
  const r = results[0] as {
    geometry: { lat: number; lng: number }
    annotations: { timezone: { name: string; offset_sec: number } }
  }
  return {
    lat: r.geometry.lat,
    lon: r.geometry.lng,
    timezone: r.annotations.timezone.name,
    offsetSec: r.annotations.timezone.offset_sec,
  }
}

// ─── Prokerala token ──────────────────────────────────────────────────────────
async function getToken(): Promise<string> {
  const resp = await fetch(`${PROKERALA_BASE}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: process.env.PROKERALA_CLIENT_ID!,
      client_secret: process.env.PROKERALA_CLIENT_SECRET!,
    }),
  })
  if (!resp.ok) throw new Error('Error obteniendo token de Prokerala')
  const data = await resp.json() as { access_token: string }
  return data.access_token
}

// ─── Datetime with offset ─────────────────────────────────────────────────────
function buildDatetime(fecha: string, hora: string, offsetSec: number): string {
  const sign = offsetSec >= 0 ? '+' : '-'
  const abs = Math.abs(offsetSec)
  const h = Math.floor(abs / 3600).toString().padStart(2, '0')
  const m = Math.floor((abs % 3600) / 60).toString().padStart(2, '0')
  return `${fecha}T${hora}:00${sign}${h}:${m}`
}

// ─── Prokerala API call ───────────────────────────────────────────────────────
async function callProkerala(
  endpoint: string,
  params: Record<string, string | number>,
  token: string,
): Promise<unknown> {
  const url = new URL(`${PROKERALA_BASE}/v2${endpoint}`)
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)))
  const resp = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!resp.ok) {
    const txt = await resp.text().catch(() => resp.statusText)
    throw new Error(`Prokerala ${endpoint}: ${txt}`)
  }
  const json = await resp.json() as { data?: unknown }
  return json.data ?? json
}

// ─── Extract readable data ────────────────────────────────────────────────────
function extractKeyData(
  nombre: string,
  fecha: string,
  hora: string,
  ciudad: string,
  geo: GeoResult,
  birthDetails: unknown,
  kundli: unknown,
  kundliAdvanced: unknown,
) {
  const bd = birthDetails as Record<string, unknown> | null
  const k = kundli as Record<string, unknown> | null
  const ka = kundliAdvanced as Record<string, unknown> | null

  const planets = (k?.planets ?? k?.planet_details ?? []) as Array<Record<string, unknown>>

  const ascendant = planets.find(
    (p) =>
      String(p.name ?? '').toLowerCase().includes('ascendant') ||
      String(p.name ?? '').toLowerCase().includes('lagna') ||
      p.id === 0,
  )

  const saturn = planets.find(
    (p) =>
      String(p.name ?? '').toLowerCase() === 'saturn' ||
      String(p.name ?? '').toLowerCase() === 'sani' ||
      p.id === 6,
  )

  return {
    nombre,
    fecha,
    hora,
    ciudad,
    timezone: geo.timezone,
    // Moon nakshatra & rashi from birth-details
    moon_nakshatra: bd?.nakshatra ?? null,
    moon_rashi: bd?.rashi ?? null,
    // Ascendant/Lagna from kundli planets
    ascendant: ascendant ?? null,
    // Saturn position
    saturn: saturn ?? null,
    // Dasha periods from kundli/advanced
    dasha_periods: ka?.dasha_periods ?? ka?.vimshottari_dasha ?? null,
    // Yogas
    yoga_details: (ka?.yoga_details ?? k?.yoga_details ?? []) as unknown[],
    // Mangal Dosha
    mangal_dosha: k?.mangal_dosha ?? null,
    // Full planets list for Claude
    all_planets: planets,
    // Raw birth details
    birth_details_raw: bd,
  }
}

// ─── Claude API — generate revelaciones ──────────────────────────────────────
async function generateRevelaciones(data: ReturnType<typeof extractKeyData>): Promise<Revelaciones> {
  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

  const prompt = `Eres AstroGuía — la voz digital de Dario Jiménez Medina, astrólogo védico profesional colombiano (Jyotish).

TONO: Gurú compasivo. Habla directamente a la persona usando su nombre. Lenguaje accesible, emotivo y espiritual. NUNCA genérico. Cada revelación debe hacer que la persona piense "¿cómo sabías eso?".

DATOS ASTROLÓGICOS DE ${data.nombre}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fecha de nacimiento: ${data.fecha}
Hora de nacimiento: ${data.hora}
Ciudad: ${data.ciudad} (${data.timezone})

Nakshatra Lunar: ${JSON.stringify(data.moon_nakshatra)}
Rashi (Signo Lunar): ${JSON.stringify(data.moon_rashi)}
Ascendente (Lagna): ${JSON.stringify(data.ascendant)}
Saturno: ${JSON.stringify(data.saturn)}
Períodos Dasha: ${JSON.stringify(data.dasha_periods)}
Yogas activos: ${JSON.stringify(data.yoga_details?.slice(0, 6))}
Dosha Mangal: ${JSON.stringify(data.mangal_dosha)}
Todos los planetas: ${JSON.stringify(data.all_planets)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GENERA EXACTAMENTE 4 REVELACIONES en español. Para cada una:
• Mínimo 5-6 oraciones sustanciales
• Usa el nombre "${data.nombre}" de forma natural (al menos una vez)
• Menciona datos técnicos reales: nombre del Nakshatra, signo, grados si disponibles, planeta del Dasha, fechas
• Cierra con una frase poética de alto impacto emocional
• Habla en segunda persona (tú/tu)
• NADA genérico — todo específico a este mapa natal

Las 4 revelaciones:
1. LAGNA: Su arquetipo central — quién es en esencia y para qué vino
2. NAKSHATRA_LUNA: El sistema operativo profundo — lo más específico y sorprendente
3. MAHADASHA: El período cósmico que vive HOY — qué planeta lo gobierna y hasta cuándo
4. SATURNO: Si está en momento de presión (Sade Sati) o libertad — el gran maestro

Responde ÚNICAMENTE con JSON válido (sin texto extra, sin markdown, sin bloques de código):
{"lagna":"...","nakshatra_luna":"...","mahadasha":"...","saturno":"..."}`

  const message = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 3500,
    messages: [{ role: 'user', content: prompt }],
  })

  const block = message.content[0]
  if (block.type !== 'text') throw new Error('Respuesta inesperada de Claude')

  const text = block.text.trim()
  // Extract JSON even if Claude wraps it in markdown
  const jsonMatch = text.match(/\{[\s\S]*\}/)
  if (!jsonMatch) throw new Error('Claude no devolvió JSON válido')

  const parsed = JSON.parse(jsonMatch[0]) as Revelaciones
  return parsed
}

// ─── Route handler ────────────────────────────────────────────────────────────
export async function POST(request: Request) {
  try {
    const body = await request.json() as {
      nombre?: string
      fecha?: string
      hora?: string
      ciudad?: string
    }
    const { nombre, fecha, hora, ciudad } = body

    if (!nombre || !fecha || !hora || !ciudad) {
      return NextResponse.json({ error: 'Todos los campos son requeridos' }, { status: 400 })
    }

    // ── Modo simulación ──────────────────────────────────────────────────────
    if (process.env.MOCK_MODE === 'true') {
      const mockData = await getMockResponse(nombre, fecha)
      return NextResponse.json(mockData)
    }

    if (!process.env.ANTHROPIC_API_KEY) {
      return NextResponse.json(
        { error: 'Falta ANTHROPIC_API_KEY en .env.local' },
        { status: 500 },
      )
    }

    // 1. Geocode
    const geo = await geocode(ciudad)

    // 2. Prokerala token
    const token = await getToken()

    // 3. Build params
    const datetime = buildDatetime(fecha, hora, geo.offsetSec)
    const base = {
      ayanamsa: AYANAMSA,
      coordinates: `${geo.lat},${geo.lon}`,
      datetime,
    }

    // 4. Parallel Prokerala calls — use allSettled so one failure doesn't block all
    const [bdResult, kundliResult, kaResult] = await Promise.allSettled([
      callProkerala('/astrology/birth-details', base, token),
      callProkerala('/astrology/kundli', base, token),
      callProkerala('/astrology/kundli/advanced', base, token),
    ])

    const birthDetails = bdResult.status === 'fulfilled' ? bdResult.value : null
    const kundli = kundliResult.status === 'fulfilled' ? kundliResult.value : null
    const kundliAdvanced = kaResult.status === 'fulfilled' ? kaResult.value : null

    // Log any failures for debugging
    if (bdResult.status === 'rejected') console.error('birth-details failed:', bdResult.reason)
    if (kundliResult.status === 'rejected') console.error('kundli failed:', kundliResult.reason)
    if (kaResult.status === 'rejected') console.error('kundli/advanced failed:', kaResult.reason)

    // 5. Extract readable data
    const extractedData = extractKeyData(nombre, fecha, hora, ciudad, geo, birthDetails, kundli, kundliAdvanced)

    // 6. Generate revelaciones with Claude
    const revelaciones = await generateRevelaciones(extractedData)

    return NextResponse.json({
      birth_data: extractedData,
      revelaciones,
      datetime,
    })
  } catch (err: unknown) {
    console.error('Error en /api/birth-data:', err)
    const message = err instanceof Error ? err.message : 'Error interno del servidor'
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
