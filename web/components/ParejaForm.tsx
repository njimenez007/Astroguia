'use client'

import { useState, FormEvent } from 'react'

export interface ParejaData {
  nombre: string
  fecha: string
  hora: string
  ciudad: string
  pareja_nombre: string
  pareja_fecha: string
  pareja_hora: string
  pareja_ciudad: string
}

interface Props {
  onSubmit: (data: ParejaData) => void
  onBack: () => void
  error?: string | null
}

const EMPTY: ParejaData = {
  nombre: '', fecha: '', hora: '', ciudad: '',
  pareja_nombre: '', pareja_fecha: '', pareja_hora: '', pareja_ciudad: '',
}

export default function ParejaForm({ onSubmit, onBack, error }: Props) {
  const [form, setForm] = useState<ParejaData>(EMPTY)
  const [focused, setFocused] = useState<string | null>(null)

  const set = (key: keyof ParejaData) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }))

  const inputClass = (key: string) =>
    `w-full bg-mystic-900/60 border rounded-xl px-4 py-3.5 text-white font-garamond text-lg
     placeholder:text-white/25 transition-all duration-200 focus:outline-none
     ${focused === key
       ? 'border-rose-400/60 shadow-[0_0_16px_rgba(251,113,133,0.08)]'
       : 'border-white/10'}`

  const valid = Object.values(form).every((v) => v.trim() !== '')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!valid) return
    onSubmit(form)
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-start px-4 py-12 relative z-10">

      {/* Header */}
      <div className="text-center mb-8 animate-fade-in">
        <button
          onClick={onBack}
          className="font-cinzel text-[10px] tracking-[0.35em] text-white/30 hover:text-gold-DEFAULT/60 uppercase transition-colors mb-6 block mx-auto"
        >
          ← Volver
        </button>
        <div className="text-4xl mb-4 select-none">💫</div>
        <h1 className="font-cinzel text-3xl md:text-4xl tracking-wide mb-2" style={{ color: '#fda4af' }}>
          Compatibilidad Védica
        </h1>
        <p className="font-cinzel text-[10px] tracking-[0.4em] text-white/30 uppercase mb-4">
          Jyotish · Kundali Matching
        </p>
        <div className="h-px bg-gradient-to-r from-transparent via-rose-400/30 to-transparent w-60 mx-auto mb-4" />
        <p className="text-white/50 font-garamond text-lg max-w-sm mx-auto leading-relaxed">
          Ingresa los datos de nacimiento exactos de ambas personas.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="w-full max-w-xl space-y-6">
        {error && (
          <div className="p-4 bg-red-950/60 border border-red-500/30 rounded-xl text-red-300 font-garamond text-base">
            ⚠️ {error}
          </div>
        )}

        {/* ── Sección 1 — Tus datos ── */}
        <div className="mystic-card rounded-2xl p-6 md:p-8 border border-rose-400/15">
          <p className="font-cinzel text-[10px] tracking-[0.4em] text-rose-300/60 uppercase mb-5">
            ✦ &nbsp; Tus datos
          </p>
          <div className="space-y-4">
            <div>
              <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">Tu nombre</label>
              <input type="text" placeholder="Tu nombre completo" value={form.nombre}
                onChange={set('nombre')} onFocus={() => setFocused('nombre')} onBlur={() => setFocused(null)}
                className={inputClass('nombre')} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">Fecha</label>
                <input type="date" value={form.fecha}
                  onChange={set('fecha')} onFocus={() => setFocused('fecha')} onBlur={() => setFocused(null)}
                  className={inputClass('fecha')} required />
              </div>
              <div>
                <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">Hora exacta</label>
                <input type="time" value={form.hora}
                  onChange={set('hora')} onFocus={() => setFocused('hora')} onBlur={() => setFocused(null)}
                  className={inputClass('hora')} required />
              </div>
            </div>
            <div>
              <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">Ciudad de nacimiento</label>
              <input type="text" placeholder="Ciudad, País" value={form.ciudad}
                onChange={set('ciudad')} onFocus={() => setFocused('ciudad')} onBlur={() => setFocused(null)}
                className={inputClass('ciudad')} required />
            </div>
          </div>
        </div>

        {/* Separador */}
        <div className="flex items-center gap-3 px-2">
          <div className="flex-1 h-px bg-white/8" />
          <span className="font-cinzel text-[10px] tracking-[0.4em] text-white/20 uppercase">y</span>
          <div className="flex-1 h-px bg-white/8" />
        </div>

        {/* ── Sección 2 — Datos de tu pareja ── */}
        <div className="mystic-card rounded-2xl p-6 md:p-8 border border-rose-400/15">
          <p className="font-cinzel text-[10px] tracking-[0.4em] text-rose-300/60 uppercase mb-5">
            ✦ &nbsp; Datos de tu pareja
          </p>
          <div className="space-y-4">
            <div>
              <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">Nombre de tu pareja</label>
              <input type="text" placeholder="Nombre completo" value={form.pareja_nombre}
                onChange={set('pareja_nombre')} onFocus={() => setFocused('pareja_nombre')} onBlur={() => setFocused(null)}
                className={inputClass('pareja_nombre')} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">Fecha</label>
                <input type="date" value={form.pareja_fecha}
                  onChange={set('pareja_fecha')} onFocus={() => setFocused('pareja_fecha')} onBlur={() => setFocused(null)}
                  className={inputClass('pareja_fecha')} required />
              </div>
              <div>
                <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">Hora exacta</label>
                <input type="time" value={form.pareja_hora}
                  onChange={set('pareja_hora')} onFocus={() => setFocused('pareja_hora')} onBlur={() => setFocused(null)}
                  className={inputClass('pareja_hora')} required />
              </div>
            </div>
            <div>
              <label className="block font-cinzel text-[10px] tracking-[0.3em] text-white/40 uppercase mb-2">Ciudad de nacimiento</label>
              <input type="text" placeholder="Ciudad, País" value={form.pareja_ciudad}
                onChange={set('pareja_ciudad')} onFocus={() => setFocused('pareja_ciudad')} onBlur={() => setFocused(null)}
                className={inputClass('pareja_ciudad')} required />
            </div>
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={!valid}
          className="w-full py-4 rounded-xl font-cinzel text-sm tracking-[0.2em] disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-[0_4px_24px_rgba(251,113,133,0.15)]"
          style={{
            background: 'linear-gradient(135deg, #be185d, #f43f5e, #fb7185, #f43f5e)',
            backgroundSize: '200% auto',
            color: '#fff',
          }}
        >
          Revelar nuestra compatibilidad &nbsp;✦
        </button>
      </form>

      <p className="mt-8 text-white/20 text-sm font-garamond text-center">
        Ayanamsa Lahiri · Swiss Ephemeris · Tradición Jyotish
      </p>
    </div>
  )
}
