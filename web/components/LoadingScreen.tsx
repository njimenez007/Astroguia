'use client'

import { useEffect, useState } from 'react'

const MESSAGES_INDIVIDUAL = [
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

const MESSAGES_PAREJA = [
  'Calculando las cartas de los dos...',
  'Posicionando los planetas de ambas cartas...',
  'Analizando la danza de sus planetas...',
  'Leyendo los Nakshatras lunares de cada uno...',
  'Consultando el Vimshottari Dasha de ambos...',
  'Midiendo la armonía de sus elementos...',
  'El cosmos está leyendo su historia...',
  'Tejiendo la revelación de su unión...',
  'Los planetas están hablando por ustedes...',
]

const PLANETS = ['☉', '☽', '♂', '♃', '♄', '♀', '☿']

interface Props {
  nombre: string
  tipo?: 'individual' | 'pareja'
}

export default function LoadingScreen({ nombre, tipo = 'individual' }: Props) {
  const [msgIdx, setMsgIdx] = useState(0)
  const [progress, setProgress] = useState(0)
  const [planetIdx, setPlanetIdx] = useState(0)

  const MESSAGES = tipo === 'pareja' ? MESSAGES_PAREJA : MESSAGES_INDIVIDUAL

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
  }, [MESSAGES.length])

  const accentColor = tipo === 'pareja' ? 'text-rose-300' : 'text-gold-DEFAULT'
  const subtitleColor = tipo === 'pareja' ? 'text-rose-300/40' : 'text-gold-DEFAULT/40'
  const barGradient = tipo === 'pareja'
    ? 'linear-gradient(90deg, #be185d, #f43f5e, #fb7185)'
    : 'linear-gradient(90deg, #a08020, #d4af37, #f0d060)'

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 relative z-10">

      {/* ── Mandala spinner ── */}
      <div className="relative w-52 h-52 mb-10">
        <div className="absolute inset-0 ring-spin">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            <circle cx="100" cy="100" r="96" fill="none"
              stroke={tipo === 'pareja' ? 'rgba(244,63,94,0.18)' : 'rgba(212,175,55,0.18)'}
              strokeWidth="1" strokeDasharray="8 6" />
          </svg>
        </div>
        <div className="absolute inset-6 ring-spin-rev">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            <circle cx="100" cy="100" r="96" fill="none"
              stroke={tipo === 'pareja' ? 'rgba(251,113,133,0.22)' : 'rgba(240,208,96,0.22)'}
              strokeWidth="1.5" strokeDasharray="4 8" />
          </svg>
        </div>
        <div className="absolute inset-12 ring-spin-med">
          <svg viewBox="0 0 200 200" className="w-full h-full">
            <circle cx="100" cy="100" r="96" fill="none"
              stroke={tipo === 'pareja' ? 'rgba(244,63,94,0.12)' : 'rgba(212,175,55,0.12)'}
              strokeWidth="1" strokeDasharray="2 10" />
          </svg>
        </div>
        <div className="absolute inset-0 ring-spin" style={{ animationDuration: '16s' }}>
          {[0, 90, 180, 270].map((deg) => (
            <div key={deg}
              className={`absolute top-0 left-1/2 -translate-x-1/2 text-xs ${
                tipo === 'pareja' ? 'text-rose-400/30' : 'text-gold-DEFAULT/30'
              }`}
              style={{ transform: `rotate(${deg}deg) translateY(4px)` }}>
              {tipo === 'pareja' ? '♡' : '✦'}
            </div>
          ))}
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-5xl ${accentColor} animate-pulse-gold select-none`}
            style={{ fontFamily: 'serif' }}>
            {PLANETS[planetIdx]}
          </span>
        </div>
      </div>

      {/* Name */}
      <h2 className={`font-cinzel text-2xl ${accentColor} tracking-wide mb-1`}>
        {nombre}
      </h2>
      <p className={`font-cinzel text-[10px] tracking-[0.4em] ${subtitleColor} uppercase mb-6`}>
        {tipo === 'pareja' ? 'Kundali Matching · Jyotish' : 'Jyotish · Astrología Védica'}
      </p>

      {/* Message */}
      <p key={msgIdx}
        className="font-garamond text-white/55 text-lg text-center mb-8 min-h-[1.8em] animate-fade-in">
        {MESSAGES[msgIdx]}
      </p>

      {/* Progress bar */}
      <div className="w-72 h-0.5 bg-mystic-700/80 rounded-full overflow-hidden mb-4">
        <div className="h-full rounded-full transition-all duration-300"
          style={{ width: `${progress}%`, background: barGradient }} />
      </div>

      <p className="text-white/25 text-sm font-garamond">
        {tipo === 'pareja'
          ? 'Calculando dos cartas — toma entre 20 y 40 segundos'
          : 'Esto toma entre 15 y 30 segundos — las estrellas no se apresuran'}
      </p>
    </div>
  )
}
