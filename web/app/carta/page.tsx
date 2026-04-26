'use client'

import { useState, useRef } from 'react'
import BloqueCard, { BloqueEstado } from '@/components/BloqueCard'

interface FormData {
  nombre: string
  fecha: string
  hora: string
  ciudad: string
}

interface BlockState {
  titulo: string
  texto: string
  estado: BloqueEstado
}

const BLOCK_TITLES = [
  'Datos Generales y Personalidad',
  'Esencia y Arquetipo del Lagna',
  'Nakshatras y Constitución Energética',
  'Arsenal Planetario y Deseos del Alma',
  'Los 8 Pilares del Destino',
]

const INIT_BLOCKS: BlockState[] = BLOCK_TITLES.map((titulo) => ({
  titulo,
  texto: '',
  estado: 'pendiente',
}))

const API_URL =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000'

type Screen = 'form' | 'carta' | 'error'

export default function CartaPage() {
  const [screen, setScreen] = useState<Screen>('form')
  const [form, setForm] = useState<FormData>({ nombre: '', fecha: '', hora: '', ciudad: '' })
  const [blocks, setBlocks] = useState<BlockState[]>(INIT_BLOCKS)
  const [nombre, setNombre] = useState('')
  const [completo, setCompleto] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentBlock, setCurrentBlock] = useState(0)
  const abortRef = useRef<AbortController | null>(null)

  const updateBlock = (num: number, patch: Partial<BlockState>) => {
    setBlocks((prev) =>
      prev.map((b, i) => (i === num - 1 ? { ...b, ...patch } : b))
    )
  }

  const handleGenerar = async () => {
    if (!form.nombre || !form.fecha || !form.hora || !form.ciudad) return

    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl

    setNombre(form.nombre)
    setBlocks(INIT_BLOCKS)
    setCompleto(false)
    setError(null)
    setCurrentBlock(0)
    setScreen('carta')

    try {
      const resp = await fetch(`${API_URL}/api/carta-completa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
        signal: ctrl.signal,
      })

      if (!resp.ok || !resp.body) {
        throw new Error(`Error del servidor: ${resp.status}`)
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let remainder = ''

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
          try {
            payload = JSON.parse(line.slice(6))
          } catch {
            continue
          }

          if (payload.e === 'block_start') {
            const num = payload.num as number
            setCurrentBlock(num)
            updateBlock(num, {
              titulo: (payload.titulo as string) || BLOCK_TITLES[num - 1],
              estado: 'generando',
              texto: '',
            })
            // Mark previous blocks done if not already
            for (let i = 1; i < num; i++) {
              setBlocks((prev) =>
                prev.map((b, idx) =>
                  idx === i - 1 && b.estado !== 'completo' ? { ...b, estado: 'completo' } : b
                )
              )
            }
          } else if (payload.e === 'c') {
            const num = payload.block as number
            const chunk = payload.t as string
            setBlocks((prev) =>
              prev.map((b, i) => (i === num - 1 ? { ...b, texto: b.texto + chunk } : b))
            )
          } else if (payload.e === 'block_done') {
            const num = payload.num as number
            updateBlock(num, { estado: 'completo' })
          } else if (payload.e === 'done') {
            setCompleto(true)
          } else if (payload.e === 'err') {
            throw new Error(payload.m as string)
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      setError(err instanceof Error ? err.message : 'Error desconocido')
      setScreen('error')
    }
  }

  // ── FORM ──────────────────────────────────────────────────────────────────
  if (screen === 'form') {
    return (
      <div className="relative min-h-screen">
        <div className="stars-bg" />
        <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 py-16">
          <div className="w-full max-w-md">
            {/* Header */}
            <div className="text-center mb-10">
              <p className="font-cinzel text-[11px] tracking-[0.45em] text-gold-DEFAULT/50 uppercase mb-3">
                AstroGuía · Jyotish
              </p>
              <h1 className="font-cinzel text-3xl gold-text tracking-wide mb-3">
                Carta Astral Védica
              </h1>
              <p className="font-garamond text-white/50 text-lg">
                Tu manual de identidad escrito en el idioma de las estrellas.
              </p>
            </div>

            {/* Form card */}
            <div className="mystic-card rounded-2xl p-8 space-y-5">
              <div>
                <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">
                  Nombre completo
                </label>
                <input
                  type="text"
                  placeholder="Tu nombre"
                  value={form.nombre}
                  onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                  className="w-full bg-white/[0.06] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base placeholder-white/25 focus:border-gold-DEFAULT/40 transition-colors"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">
                    Fecha de nacimiento
                  </label>
                  <input
                    type="date"
                    value={form.fecha}
                    onChange={(e) => setForm((f) => ({ ...f, fecha: e.target.value }))}
                    className="w-full bg-white/[0.06] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base focus:border-gold-DEFAULT/40 transition-colors"
                  />
                </div>
                <div>
                  <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">
                    Hora de nacimiento
                  </label>
                  <input
                    type="time"
                    value={form.hora}
                    onChange={(e) => setForm((f) => ({ ...f, hora: e.target.value }))}
                    className="w-full bg-white/[0.06] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base focus:border-gold-DEFAULT/40 transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">
                  Ciudad de nacimiento
                </label>
                <input
                  type="text"
                  placeholder="Ciudad, País"
                  value={form.ciudad}
                  onChange={(e) => setForm((f) => ({ ...f, ciudad: e.target.value }))}
                  className="w-full bg-white/[0.06] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base placeholder-white/25 focus:border-gold-DEFAULT/40 transition-colors"
                />
              </div>

              <button
                onClick={handleGenerar}
                disabled={!form.nombre || !form.fecha || !form.hora || !form.ciudad}
                className="btn-gold w-full py-4 rounded-xl text-xs tracking-[0.25em] mt-2 disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_4px_24px_rgba(212,175,55,0.15)]"
              >
                Generar Carta Astral &nbsp;✦
              </button>
            </div>

            <p className="text-center text-white/20 font-garamond text-sm mt-6">
              Astrología Védica · Jyotish · Sistema Parashara
            </p>
          </div>
        </div>
      </div>
    )
  }

  // ── ERROR ─────────────────────────────────────────────────────────────────
  if (screen === 'error') {
    return (
      <div className="relative min-h-screen flex items-center justify-center px-4">
        <div className="stars-bg" />
        <div className="relative z-10 text-center max-w-sm">
          <p className="font-cinzel text-gold-DEFAULT text-xl mb-3">Error</p>
          <p className="font-garamond text-white/60 mb-6">{error}</p>
          <button
            onClick={() => setScreen('form')}
            className="btn-gold px-8 py-3 rounded-xl text-xs tracking-widest"
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  // ── CARTA (generando + completa) ──────────────────────────────────────────
  const blocksCompletos = blocks.filter((b) => b.estado === 'completo').length

  return (
    <div className="relative min-h-screen">
      <div className="stars-bg" />

      {/* Sticky top bar */}
      <div className="sticky top-0 z-50 bg-mystic-900/90 backdrop-blur-md border-b border-white/[0.07]">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-4">
          <button
            onClick={() => { abortRef.current?.abort(); setScreen('form') }}
            className="font-cinzel text-[10px] tracking-[0.3em] text-white/30 hover:text-gold-DEFAULT/70 uppercase transition-colors"
          >
            ← Volver
          </button>
          <span className="font-cinzel text-[10px] tracking-[0.35em] text-gold-DEFAULT/40 uppercase flex-1 text-center">
            AstroGuía · Carta Astral
          </span>
          {/* Progress dots */}
          <div className="flex items-center gap-1.5">
            {blocks.map((b, i) => (
              <button
                key={i}
                onClick={() => {
                  document.getElementById(`bloque-${i + 1}`)?.scrollIntoView({ behavior: 'smooth' })
                }}
                title={b.titulo}
                className={`w-2 h-2 rounded-full transition-all ${
                  b.estado === 'completo'
                    ? 'bg-gold-DEFAULT'
                    : b.estado === 'generando'
                    ? 'bg-gold-DEFAULT/50 animate-pulse'
                    : 'bg-white/15'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 py-10">

        {/* Header cliente */}
        <div className="text-center mb-12">
          <p className="font-cinzel text-[10px] tracking-[0.45em] text-gold-DEFAULT/40 uppercase mb-4">
            Lectura de Primera Cita · Jyotish
          </p>
          <h1 className="font-cinzel text-3xl md:text-4xl gold-text tracking-wide mb-2">
            {nombre}
          </h1>
          <p className="font-garamond text-white/40 text-lg">
            {form.fecha} &nbsp;·&nbsp; {form.hora} &nbsp;·&nbsp; {form.ciudad}
          </p>

          {completo ? (
            <div className="mt-6 inline-flex items-center gap-2 bg-gold-DEFAULT/10 border border-gold-DEFAULT/25 rounded-full px-5 py-2">
              <span className="text-gold-DEFAULT text-xs">✦</span>
              <span className="font-cinzel text-[10px] tracking-[0.35em] text-gold-DEFAULT uppercase">
                Lectura Completa
              </span>
              <span className="text-gold-DEFAULT text-xs">✦</span>
            </div>
          ) : (
            <div className="mt-6 inline-flex items-center gap-2">
              <span className="font-garamond text-white/35 text-base">
                Generando bloque {currentBlock} de 5
              </span>
              <span className="inline-block w-1 h-4 bg-gold-DEFAULT/50 animate-pulse rounded" />
            </div>
          )}

          <div className="gold-divider mt-8" />
        </div>

        {/* Bloques */}
        {blocks.map((b, i) => (
          <BloqueCard
            key={i}
            num={i + 1}
            titulo={b.titulo}
            texto={b.texto}
            estado={b.estado}
          />
        ))}

        {/* Footer de la lectura */}
        {completo && (
          <div className="text-center mt-8 mb-16">
            <div className="gold-divider mb-8" />
            <p className="font-cinzel text-[10px] tracking-[0.4em] text-gold-DEFAULT/40 uppercase mb-2">
              ✦ &nbsp; Fin de la Lectura &nbsp; ✦
            </p>
            <p className="font-garamond text-white/30 text-base">
              Dario Jiménez Medina · Jyotish · Bogotá, Colombia
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
