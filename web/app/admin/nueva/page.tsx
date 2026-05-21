'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import AdminNav from '@/components/AdminNav'
import BloqueCard, { BloqueEstado } from '@/components/BloqueCard'

type Tipo = 'carta' | 'predicciones' | 'compatibilidad'
type Step = 'form' | 'reading'

interface BlockState {
  titulo: string
  texto: string
  estado: BloqueEstado
}

const BLOCK_TITLES: Record<Tipo, string[]> = {
  carta: [
    'Datos Generales y Personalidad',
    'Esencia y Arquetipo del Lagna',
    'Nakshatras y Constitución Energética',
    'Arsenal Planetario y Deseos del Alma',
    'Los 8 Pilares del Destino',
  ],
  predicciones: [
    'El Ciclo de Saturno — Tu Terreno Actual',
    'El Gran Período — Tu Mahadasha',
    'El Momento Interno — Tu Antardasha',
    'El Mapa de los Próximos 24 Meses',
    'Tu Brújula Cósmica — Estrategia e Integración',
  ],
  compatibilidad: [
    'La Unión en el Cosmos — Primera Vista',
    'Los Ascendentes — Las Dos Personalidades',
    'Las Lunas — La Química Emocional',
    'Los Pilares de la Relación',
    'Los Ciclos Compartidos — El Futuro de la Unión',
  ],
}

const TIPO_META = {
  carta: {
    label: 'Carta Astral',
    desc: 'Manual completo de identidad — 5 capítulos',
    icon: '✦',
    border: 'border-gold-DEFAULT/30',
    bg: 'bg-gold-DEFAULT/6',
    text: 'text-gold-DEFAULT',
    endpoint: '/api/carta-completa',
  },
  predicciones: {
    label: 'Predicciones',
    desc: 'Sade Sati + Dashas — Ciclos y timing',
    icon: '⏳',
    border: 'border-violet-500/30',
    bg: 'bg-violet-500/6',
    text: 'text-violet-400',
    endpoint: '/api/predicciones',
  },
  compatibilidad: {
    label: 'Compatibilidad',
    desc: 'Kundali Matching completo — Pareja',
    icon: '♡',
    border: 'border-rose-400/30',
    bg: 'bg-rose-400/6',
    text: 'text-rose-400',
    endpoint: '/api/compatibilidad-completa',
  },
}

const CHAPTER_ROMANS = ['I', 'II', 'III', 'IV', 'V']

const API_URL =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000'

function makeInitBlocks(tipo: Tipo): BlockState[] {
  return BLOCK_TITLES[tipo].map((titulo) => ({ titulo, texto: '', estado: 'pendiente' }))
}

export default function NuevaPage() {
  const router = useRouter()
  const [userEmail, setUserEmail] = useState('')

  const [step, setStep] = useState<Step>('form')
  const [tipo, setTipo] = useState<Tipo>('carta')

  // Form fields
  const [nombre, setNombre] = useState('')
  const [fecha, setFecha] = useState('')
  const [hora, setHora] = useState('')
  const [ciudad, setCiudad] = useState('')
  const [parejaNombre, setParejaNombre] = useState('')
  const [parejaFecha, setParejaFecha] = useState('')
  const [parejaHora, setParejaHora] = useState('')
  const [parejaCiudad, setParejaCiudad] = useState('')

  // Generation state
  const [blocks, setBlocks] = useState<BlockState[]>(makeInitBlocks(tipo))
  const [currentBlock, setCurrentBlock] = useState(0)
  const [completo, setCompleto] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [savedId, setSavedId] = useState<string | null>(null)

  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    const supabase = createClient()
    void supabase.auth.getUser().then((res: { data: { user: { email?: string } | null } }) => {
      setUserEmail(res.data.user?.email ?? '')
    })
  }, [])

  const handleTipoChange = (t: Tipo) => {
    setTipo(t)
    setBlocks(makeInitBlocks(t))
    setError(null)
  }

  const formValid =
    nombre.trim() &&
    fecha &&
    hora &&
    ciudad.trim() &&
    (tipo !== 'compatibilidad' ||
      (parejaNombre.trim() && parejaFecha && parejaHora && parejaCiudad.trim()))

  const handleGenerar = async () => {
    if (!formValid) return

    setBlocks(makeInitBlocks(tipo))
    setCurrentBlock(0)
    setCompleto(false)
    setError(null)
    setSavedId(null)
    setStep('reading')

    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl

    // Fetch custom system prompt if one has been saved for this tipo
    const supabase = createClient()
    const { data: promptRow } = await supabase
      .from('prompts')
      .select('contenido')
      .eq('tipo', tipo)
      .single()
    const customSystem = promptRow?.contenido || null

    const body =
      tipo === 'compatibilidad'
        ? { nombre, fecha, hora, ciudad, pareja_nombre: parejaNombre, pareja_fecha: parejaFecha, pareja_hora: parejaHora, pareja_ciudad: parejaCiudad, custom_system: customSystem }
        : { nombre, fecha, hora, ciudad, custom_system: customSystem }

    const endpoint = TIPO_META[tipo].endpoint

    try {
      const resp = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: ctrl.signal,
      })

      if (!resp.ok || !resp.body) throw new Error(`Error ${resp.status}`)

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let remainder = ''
      const finalBlocks: BlockState[] = makeInitBlocks(tipo)

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const raw = decoder.decode(value, { stream: true })
        const text = remainder + raw
        const lines = text.split('\n')
        remainder = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          let payload: Record<string, unknown>
          try { payload = JSON.parse(line.slice(6)) } catch { continue }

          if (payload.e === 'block_start') {
            const num = payload.num as number
            setCurrentBlock(num)
            const titulo = (payload.titulo as string) || BLOCK_TITLES[tipo][num - 1]
            finalBlocks[num - 1] = { titulo, texto: '', estado: 'generando' }
            for (let i = 0; i < num - 1; i++) {
              if (finalBlocks[i].estado !== 'completo') finalBlocks[i] = { ...finalBlocks[i], estado: 'completo' }
            }
            setBlocks([...finalBlocks])
          } else if (payload.e === 'c') {
            const num = payload.block as number
            finalBlocks[num - 1].texto += payload.t as string
            setBlocks([...finalBlocks])
          } else if (payload.e === 'block_done') {
            const num = payload.num as number
            finalBlocks[num - 1].estado = 'completo'
            setBlocks([...finalBlocks])
          } else if (payload.e === 'done') {
            setCompleto(true)
            // Auto-save to Supabase
            await saveToSupabase(finalBlocks)
          } else if (payload.e === 'err') {
            throw new Error(payload.m as string)
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      setError(err instanceof Error ? err.message : 'Error desconocido')
    }
  }

  const saveToSupabase = async (finalBlocks: BlockState[]) => {
    setSaving(true)
    try {
      const supabase = createClient()

      // Create cliente
      const { data: cliente, error: cErr } = await supabase
        .from('clientes')
        .insert({ nombre, fecha_nacimiento: fecha, hora_nacimiento: hora, ciudad })
        .select('id')
        .single()

      if (cErr) throw cErr

      // Create lectura
      const lecturaData: Record<string, unknown> = {
        cliente_id: cliente.id,
        tipo,
        estado: 'completo',
        contenido: finalBlocks.map((b, i) => ({
          num: i + 1,
          titulo: b.titulo,
          texto: b.texto,
        })),
      }

      if (tipo === 'compatibilidad') {
        lecturaData.pareja_nombre = parejaNombre
        lecturaData.pareja_fecha = parejaFecha
        lecturaData.pareja_hora = parejaHora
        lecturaData.pareja_ciudad = parejaCiudad
      }

      const { data: lectura, error: lErr } = await supabase
        .from('lecturas')
        .insert(lecturaData)
        .select('id')
        .single()

      if (lErr) throw lErr
      setSavedId(lectura.id)
    } catch (e) {
      console.error('Error guardando en Supabase:', e)
    } finally {
      setSaving(false)
    }
  }

  const handlePrint = () => {
    window.print()
  }

  // ── FORM ──────────────────────────────────────────────────────────────────
  if (step === 'form') {
    return (
      <div className="relative min-h-screen">
        <div className="stars-bg" aria-hidden="true" />
        <AdminNav userEmail={userEmail} title="Nueva Lectura" />

        <div className="relative z-10 max-w-2xl mx-auto px-4 py-10">

          {/* Tipo selector */}
          <div className="mb-8">
            <p className="font-cinzel text-[10px] tracking-[0.4em] text-gold-DEFAULT/40 uppercase mb-4">
              Tipo de lectura
            </p>
            <div className="grid grid-cols-3 gap-3">
              {(Object.keys(TIPO_META) as Tipo[]).map((t) => {
                const meta = TIPO_META[t]
                const selected = tipo === t
                return (
                  <button
                    key={t}
                    onClick={() => handleTipoChange(t)}
                    className={`mystic-card rounded-xl p-4 border text-center transition-all ${
                      selected
                        ? `${meta.border} ${meta.bg}`
                        : 'border-white/8 hover:border-white/15'
                    }`}
                  >
                    <div className={`text-xl mb-2 ${selected ? meta.text : 'text-white/30'}`}>
                      {meta.icon}
                    </div>
                    <p className={`font-cinzel text-[10px] tracking-[0.25em] uppercase ${selected ? meta.text : 'text-white/40'}`}>
                      {meta.label}
                    </p>
                    <p className="font-garamond text-white/25 text-xs mt-1 leading-snug">
                      {meta.desc}
                    </p>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Client form */}
          <div className="mystic-card rounded-2xl border border-white/10 p-8 space-y-5">
            <div>
              <p className="font-cinzel text-[10px] tracking-[0.4em] text-gold-DEFAULT/38 uppercase mb-4">
                Datos del cliente
              </p>
              <div className="space-y-4">
                <div>
                  <label className="block font-cinzel text-[9px] tracking-[0.35em] text-white/30 uppercase mb-1.5">
                    Nombre completo
                  </label>
                  <input
                    type="text"
                    placeholder="Nombre del cliente"
                    value={nombre}
                    onChange={e => setNombre(e.target.value)}
                    className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base placeholder-white/20 focus:border-gold-DEFAULT/35 outline-none transition-colors"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-cinzel text-[9px] tracking-[0.35em] text-white/30 uppercase mb-1.5">
                      Fecha
                    </label>
                    <input
                      type="date"
                      value={fecha}
                      onChange={e => setFecha(e.target.value)}
                      className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base focus:border-gold-DEFAULT/35 outline-none transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block font-cinzel text-[9px] tracking-[0.35em] text-white/30 uppercase mb-1.5">
                      Hora
                    </label>
                    <input
                      type="time"
                      value={hora}
                      onChange={e => setHora(e.target.value)}
                      className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base focus:border-gold-DEFAULT/35 outline-none transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block font-cinzel text-[9px] tracking-[0.35em] text-white/30 uppercase mb-1.5">
                    Ciudad de nacimiento
                  </label>
                  <input
                    type="text"
                    placeholder="Ciudad, País"
                    value={ciudad}
                    onChange={e => setCiudad(e.target.value)}
                    className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base placeholder-white/20 focus:border-gold-DEFAULT/35 outline-none transition-colors"
                  />
                </div>
              </div>
            </div>

            {/* Pareja form — solo para compatibilidad */}
            {tipo === 'compatibilidad' && (
              <div className="pt-4 border-t border-rose-400/10">
                <p className="font-cinzel text-[10px] tracking-[0.4em] text-rose-400/38 uppercase mb-4">
                  Datos de la pareja
                </p>
                <div className="space-y-4">
                  <div>
                    <label className="block font-cinzel text-[9px] tracking-[0.35em] text-white/30 uppercase mb-1.5">
                      Nombre completo
                    </label>
                    <input
                      type="text"
                      placeholder="Nombre de la pareja"
                      value={parejaNombre}
                      onChange={e => setParejaNombre(e.target.value)}
                      className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base placeholder-white/20 focus:border-rose-400/35 outline-none transition-colors"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block font-cinzel text-[9px] tracking-[0.35em] text-white/30 uppercase mb-1.5">Fecha</label>
                      <input type="date" value={parejaFecha} onChange={e => setParejaFecha(e.target.value)}
                        className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base focus:border-rose-400/35 outline-none transition-colors" />
                    </div>
                    <div>
                      <label className="block font-cinzel text-[9px] tracking-[0.35em] text-white/30 uppercase mb-1.5">Hora</label>
                      <input type="time" value={parejaHora} onChange={e => setParejaHora(e.target.value)}
                        className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base focus:border-rose-400/35 outline-none transition-colors" />
                    </div>
                  </div>
                  <div>
                    <label className="block font-cinzel text-[9px] tracking-[0.35em] text-white/30 uppercase mb-1.5">Ciudad de nacimiento</label>
                    <input type="text" placeholder="Ciudad, País" value={parejaCiudad} onChange={e => setParejaCiudad(e.target.value)}
                      className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base placeholder-white/20 focus:border-rose-400/35 outline-none transition-colors" />
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={handleGenerar}
              disabled={!formValid}
              className="btn-gold w-full py-4 rounded-xl text-xs tracking-[0.22em] disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_4px_24px_rgba(212,175,55,0.15)] mt-2"
            >
              Generar Informe &nbsp;✦
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── READING (generating + complete) ───────────────────────────────────────
  const meta = TIPO_META[tipo]

  return (
    <div className="relative min-h-screen">
      <div className="stars-bg" aria-hidden="true" />

      {/* Sticky nav */}
      <div className="sticky top-0 z-50 bg-mystic-900/95 backdrop-blur-md border-b border-white/[0.06] print:hidden">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => { abortRef.current?.abort(); setStep('form') }}
            className="font-cinzel text-[10px] tracking-[0.3em] text-white/45 hover:text-gold-DEFAULT transition-colors border border-white/12 hover:border-gold-DEFAULT/35 px-3 py-1.5 rounded-full"
          >
            ← Editar
          </button>

          <span className="font-cinzel text-[9px] tracking-[0.35em] text-gold-DEFAULT/30 uppercase flex-1 text-center truncate">
            {meta.label} · {nombre}
          </span>

          {/* Chapter progress */}
          <div className="flex items-center gap-2.5">
            {blocks.map((b, i) => (
              <button
                key={i}
                onClick={() => document.getElementById(`bloque-${i + 1}`)?.scrollIntoView({ behavior: 'smooth' })}
                className={`font-cinzel text-[9px] tracking-widest transition-all ${
                  b.estado === 'completo' ? 'text-gold-DEFAULT' :
                  b.estado === 'generando' ? 'text-gold-DEFAULT/50 animate-pulse' :
                  'text-white/18'
                }`}
              >
                {CHAPTER_ROMANS[i]}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 py-12">

        {/* Cover header */}
        <div className="text-center mb-14 animate-fade-in print:mb-10">
          <div className={`text-2xl mb-4 tracking-widest select-none ${meta.text} opacity-40`}>
            {tipo === 'compatibilidad' ? '♡ · ✦ · ♡' : '☽ · ✦ · ☾'}
          </div>
          <p className="font-cinzel text-[10px] tracking-[0.5em] text-gold-DEFAULT/35 uppercase mb-3">
            {meta.label} · Jyotish
          </p>
          <h1 className="font-cinzel text-4xl md:text-5xl gold-text tracking-wide mb-2">
            {tipo === 'compatibilidad' ? `${nombre} y ${parejaNombre}` : nombre}
          </h1>
          <p className="font-garamond text-white/30 text-base">
            {fecha}{hora ? ` · ${hora}` : ''}{ciudad ? ` · ${ciudad}` : ''}
          </p>
          <div className="gold-divider mt-8 mb-8" />

          {/* Status */}
          {completo ? (
            <div className="flex items-center justify-center gap-3 flex-wrap">
              <div className="inline-flex items-center gap-2 bg-gold-DEFAULT/8 border border-gold-DEFAULT/20 rounded-full px-5 py-2">
                <span className="text-gold-DEFAULT text-xs">✦</span>
                <span className="font-cinzel text-[10px] tracking-[0.4em] text-gold-DEFAULT uppercase">
                  {saving ? 'Guardando...' : savedId ? 'Guardado ✓' : 'Informe Completo'}
                </span>
                <span className="text-gold-DEFAULT text-xs">✦</span>
              </div>
              <button
                onClick={handlePrint}
                className="font-cinzel text-[10px] tracking-[0.3em] text-white/45 hover:text-gold-DEFAULT border border-white/12 hover:border-gold-DEFAULT/35 px-4 py-2 rounded-full transition-colors print:hidden"
              >
                Imprimir / PDF
              </button>
              {savedId && (
                <button
                  onClick={() => router.push('/admin/dashboard')}
                  className="font-cinzel text-[10px] tracking-[0.3em] text-white/35 hover:text-white/60 border border-white/10 px-4 py-2 rounded-full transition-colors print:hidden"
                >
                  Ver historial
                </button>
              )}
            </div>
          ) : error ? (
            <div className="text-center">
              <p className="font-garamond text-red-400/70 text-base mb-3">{error}</p>
              <button
                onClick={() => setStep('form')}
                className="font-cinzel text-[10px] tracking-[0.3em] text-white/40 border border-white/12 px-4 py-2 rounded-full"
              >
                Volver al formulario
              </button>
            </div>
          ) : (
            <div className="inline-flex items-center gap-2">
              <span className="font-garamond text-white/28 text-base">
                Generando capítulo {CHAPTER_ROMANS[currentBlock - 1] ?? '—'} de V
              </span>
              <span className="inline-block w-0.5 h-4 bg-gold-DEFAULT/40 animate-pulse rounded" />
            </div>
          )}
        </div>

        {/* Chapters */}
        {blocks.map((b, i) => (
          <BloqueCard
            key={i}
            num={i + 1}
            titulo={b.titulo}
            texto={b.texto}
            estado={b.estado}
          />
        ))}

        {/* Footer */}
        {completo && (
          <div className="text-center mt-4 mb-16 print:mt-8">
            <div className="gold-divider mb-8" />
            <p className="font-cinzel text-[9px] tracking-[0.5em] text-gold-DEFAULT/30 uppercase mb-2">
              Fin de la Lectura
            </p>
            <p className="font-garamond text-white/22 text-base">
              Dario Jiménez Medina · Jyotish · Bogotá, Colombia
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
