'use client'

import { useEffect, useState } from 'react'

const MESSAGES = [
  'Geocodificando tu lugar de nacimiento...',
  'Calculando tu Lagna con Ayanamsa Lahiri...',
  'Posicionando los Nava Grahas...',
  'Leyendo el Nakshatra de tu Luna...',
  'Consultando el Vimshottari Dasha...',
  'Analizando la posición de Saturno...',
  'Verificando Yogas activos en tu carta...',
  'Tejiendo tus revelaciones védicas...',
  'Las estrellas están hablando...',
]

const PLANETS = ['☉', '☽', '♂', '♃', '♄', '♀', '☿']

interface Props {
  nombre: string
}

export default function LoadingScreen({ nombre }: Props) {
  const [msgIdx, setMsgIdx] = useState(0)
  const [progress, setProgress] = useState(0)
  const [planetIdx, setPlanetIdx] = useState(0)

  useEffect(() => {
    const msgTimer = setInterval(
      () => setMsgIdx((i) => Math.min(i + 1, MESSAGES.length - 1)),
      3000,
    )
    const planetTimer = setInterval(
      () => setPlanetIdx((i) => (i + 1) % PLANETS.length),
      800,
    )
    const progressTimer = setInterval(
      () => setProgress((p) => Math.min(p + 1.2, 92)),
      200,
    )
    return () => {
      clearInterval(msgTimer)
      clearInterval(planetTimer)
      clearInterval(progressTimer)
    }
  }, [])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 relative z-10">

      {/* ── Mandala spinner ── */}
      <div className="relative w-52 h-52 mb-10">
        {/* Outer ring */}
        <div className="absolute inset-0 ring-spin">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            <circle
              cx="100" cy="100" r="96"
              fill="none"
              stroke="rgba(212,175,55,0.18)"
              strokeWidth="1"
              strokeDasharray="8 6"
            />
          </svg>
        </div>

        {/* Middle ring */}
        <div className="absolute inset-6 ring-spin-rev">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            <circle
              cx="100" cy="100" r="96"
              fill="none"
              stroke="rgba(240,208,96,0.22)"
              strokeWidth="1.5"
              strokeDasharray="4 8"
            />
          </svg>
        </div>

        {/* Inner ring */}
        <div className="absolute inset-12 ring-spin-med">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            <circle
              cx="100" cy="100" r="96"
              fill="none"
              stroke="rgba(212,175,55,0.12)"
              strokeWidth="1"
              strokeDasharray="2 10"
            />
          </svg>
        </div>

        {/* Corner diamonds */}
        <div className="absolute inset-0 ring-spin" style={{ animationDuration: '16s' }}>
          {[0, 90, 180, 270].map((deg) => (
            <div
              key={deg}
              className="absolute top-0 left-1/2 -translate-x-1/2 text-gold-DEFAULT/30 text-xs"
              style={{ transform: `rotate(${deg}deg) translateY(4px)` }}
            >
              ✦
            </div>
          ))}
        </div>

        {/* Center planet symbol */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span
            className="text-5xl text-gold-DEFAULT animate-pulse-gold select-none"
            style={{ fontFamily: 'serif' }}
          >
            {PLANETS[planetIdx]}
          </span>
        </div>
      </div>

      {/* ── Name ── */}
      <h2 className="font-cinzel text-2xl text-gold-DEFAULT tracking-wide mb-1">
        {nombre}
      </h2>
      <p className="font-cinzel text-[10px] tracking-[0.4em] text-gold-DEFAULT/40 uppercase mb-6">
        Jyotish · Astrología Védica
      </p>

      {/* ── Message ── */}
      <p
        key={msgIdx}
        className="font-garamond text-white/55 text-lg text-center mb-8 min-h-[1.8em] animate-fade-in"
      >
        {MESSAGES[msgIdx]}
      </p>

      {/* ── Progress bar ── */}
      <div className="w-72 h-0.5 bg-mystic-700/80 rounded-full overflow-hidden mb-4">
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${progress}%`,
            background: 'linear-gradient(90deg, #a08020, #d4af37, #f0d060)',
          }}
        />
      </div>

      <p className="text-white/25 text-sm font-garamond">
        Esto toma entre 15 y 30 segundos — las estrellas no se apresuran
      </p>
    </div>
  )
}
