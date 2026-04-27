'use client'

import { useState, FormEvent } from 'react'

export interface FormData {
  nombre: string
  fecha: string
  hora: string
  ciudad: string
}

interface Props {
  onSubmit: (data: FormData) => void
  error?: string | null
  onBack?: () => void
}

export default function LandingForm({ onSubmit, error, onBack }: Props) {
  const [form, setForm] = useState<FormData>({ nombre: '', fecha: '', hora: '', ciudad: '' })
  const [focused, setFocused] = useState<string | null>(null)

  const set = (key: keyof FormData) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }))

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!form.nombre || !form.fecha || !form.hora || !form.ciudad) return
    onSubmit(form)
  }

  const inputClass = (key: string) =>
    `w-full bg-mystic-900/60 border rounded-xl px-4 py-3.5 text-white font-garamond text-lg
     placeholder:text-white/25 transition-all duration-200 focus:outline-none
     ${focused === key ? 'border-gold-DEFAULT/70 shadow-[0_0_16px_rgba(212,175,55,0.12)]' : 'border-gold-DEFAULT/18'}`

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-16 relative z-10">

      {/* ── Header ── */}
      <div className="text-center mb-10 animate-fade-in">
        {onBack && (
          <button
            onClick={onBack}
            className="font-cinzel text-[10px] tracking-[0.35em] text-white/30 hover:text-gold-DEFAULT/60 uppercase transition-colors mb-6 block mx-auto"
          >
            ← Volver
          </button>
        )}
        <div className="text-4xl mb-4 tracking-widest text-gold-DEFAULT/60 select-none">
          ☽ &nbsp; ✦ &nbsp; ☾
        </div>
        <h1 className="font-cinzel text-5xl md:text-6xl gold-text tracking-[0.12em] mb-2">
          AstroGuía
        </h1>
        <p className="font-cinzel text-xs tracking-[0.4em] text-gold-DEFAULT/45 uppercase mb-6">
          Jyotish · Astrología Védica
        </p>
        <div className="gold-divider w-60 mx-auto mb-6" />
        <p className="text-white/60 font-garamond text-xl max-w-sm mx-auto leading-relaxed">
          Ingresa los datos exactos de tu nacimiento y descubre lo que las estrellas revelan.
        </p>
      </div>

      {/* ── Form card ── */}
      <div
        className="mystic-card rounded-2xl p-8 md:p-10 w-full max-w-md shadow-[0_8px_60px_rgba(0,0,0,0.6)]"
        style={{ animationDelay: '0.2s' }}
      >
        {error && (
          <div className="mb-6 p-4 bg-red-950/60 border border-red-500/30 rounded-xl text-red-300 font-garamond text-base leading-relaxed">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">

          {/* Nombre */}
          <div>
            <label className="block font-cinzel text-[10px] tracking-[0.35em] text-gold-DEFAULT/70 mb-2 uppercase">
              Nombre
            </label>
            <input
              type="text"
              placeholder="María Fernanda García"
              value={form.nombre}
              onChange={set('nombre')}
              onFocus={() => setFocused('nombre')}
              onBlur={() => setFocused(null)}
              className={inputClass('nombre')}
              required
              autoComplete="name"
            />
          </div>

          {/* Fecha */}
          <div>
            <label className="block font-cinzel text-[10px] tracking-[0.35em] text-gold-DEFAULT/70 mb-2 uppercase">
              Fecha de nacimiento
            </label>
            <input
              type="date"
              value={form.fecha}
              onChange={set('fecha')}
              onFocus={() => setFocused('fecha')}
              onBlur={() => setFocused(null)}
              className={inputClass('fecha')}
              required
            />
          </div>

          {/* Hora */}
          <div>
            <label className="block font-cinzel text-[10px] tracking-[0.35em] text-gold-DEFAULT/70 mb-2 uppercase">
              Hora exacta de nacimiento
            </label>
            <input
              type="time"
              value={form.hora}
              onChange={set('hora')}
              onFocus={() => setFocused('hora')}
              onBlur={() => setFocused(null)}
              className={inputClass('hora')}
              required
            />
            <p className="mt-1.5 text-white/28 text-xs font-garamond leading-snug">
              La hora exacta define tu Lagna (Ascendente)
            </p>
          </div>

          {/* Ciudad */}
          <div>
            <label className="block font-cinzel text-[10px] tracking-[0.35em] text-gold-DEFAULT/70 mb-2 uppercase">
              Ciudad de nacimiento
            </label>
            <input
              type="text"
              placeholder="Bogotá, Colombia"
              value={form.ciudad}
              onChange={set('ciudad')}
              onFocus={() => setFocused('ciudad')}
              onBlur={() => setFocused(null)}
              className={inputClass('ciudad')}
              required
              autoComplete="off"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="btn-gold w-full mt-3 py-4 rounded-xl text-sm tracking-[0.2em] shadow-[0_4px_24px_rgba(212,175,55,0.2)]"
          >
            Revelar mi Carta Védica &nbsp;✦
          </button>
        </form>
      </div>

      {/* ── Footer note ── */}
      <p className="mt-8 text-white/25 text-sm font-garamond text-center max-w-xs leading-relaxed">
        Cálculos con Ayanamsa Lahiri · Swiss Ephemeris · Prokerala API
      </p>
    </div>
  )
}
