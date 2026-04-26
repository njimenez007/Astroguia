'use client'

import { useEffect, useState } from 'react'
import type { RevStream } from '@/app/page'

interface Props {
  nombre: string
  revs: RevStream[]
  streaming: boolean
  onCTA: () => void
}

const CARD_META = [
  {
    icon: '🪐',
    subtitle: 'El ciclo de Saturno · Tu gran maestro',
    accent: 'border-slate-500/30',
    glow: 'rgba(100,116,139,0.07)',
  },
  {
    icon: '⏳',
    subtitle: 'El período cósmico que vives hoy',
    accent: 'border-purple-500/25',
    glow: 'rgba(168,85,247,0.06)',
  },
  {
    icon: '✨',
    subtitle: 'El talento que el cielo te confió',
    accent: 'border-emerald-500/25',
    glow: 'rgba(16,185,129,0.05)',
  },
  {
    icon: '🌙',
    subtitle: 'Tu corazón secreto · El sistema operativo del alma',
    accent: 'border-indigo-500/25',
    glow: 'rgba(99,102,241,0.06)',
  },
]

function Cursor() {
  return (
    <span
      className="inline-block w-[2px] h-[1.1em] bg-gold-DEFAULT/70 ml-0.5 align-middle animate-pulse"
      aria-hidden="true"
    />
  )
}

function RevCard({
  rev,
  meta,
  isActive,
  delay,
}: {
  rev: RevStream
  meta: (typeof CARD_META)[number]
  isActive: boolean
  delay: number
}) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), delay)
    return () => clearTimeout(t)
  }, [delay])

  const hasPromesa = rev.promesa.length > 0
  const promesaText = rev.promesa.replace(/^✦\s*/, '').trim()

  return (
    <div
      className={`mystic-card mystic-card-hover rounded-2xl p-6 md:p-8 border ${meta.accent}
        transition-all duration-700
        ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'}`}
      style={{ boxShadow: `inset 0 0 40px ${meta.glow}` }}
    >
      <div className="flex gap-4">
        <span className="text-3xl flex-shrink-0 mt-0.5 select-none">{meta.icon}</span>
        <div className="min-w-0 w-full">
          {/* Title */}
          <h2 className="font-cinzel text-gold-DEFAULT text-lg tracking-wide leading-snug">
            {rev.titulo || <span className="opacity-0">…</span>}
          </h2>
          <p className="font-cinzel text-[9px] tracking-[0.38em] text-gold-DEFAULT/38 uppercase mb-4">
            {meta.subtitle}
          </p>

          {/* Body */}
          <p className="text-white/82 font-garamond text-[1.08rem] leading-[1.75] whitespace-pre-wrap">
            {rev.cuerpo}
            {isActive && !hasPromesa && <Cursor />}
          </p>

          {/* Promise */}
          {hasPromesa && (
            <div className="mt-5 pt-4 border-t border-gold-DEFAULT/10">
              <p className="text-gold-DEFAULT/65 font-garamond text-[0.98rem] italic leading-relaxed">
                ✦ {promesaText}
                {isActive && <Cursor />}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Revelaciones({ nombre, revs, streaming, onCTA }: Props) {
  const [ctaVisible, setCtaVisible] = useState(false)

  useEffect(() => {
    if (!streaming && revs.length === 4) {
      const t = setTimeout(() => setCtaVisible(true), 900)
      return () => clearTimeout(t)
    }
  }, [streaming, revs.length])

  return (
    <div className="min-h-screen px-4 py-16 relative z-10">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10 animate-fade-in">
          <div className="text-3xl mb-3 tracking-widest text-gold-DEFAULT/50 select-none">
            ☽ &nbsp; ✦ &nbsp; ☾
          </div>
          <h1 className="font-cinzel text-3xl md:text-4xl gold-text tracking-wide mb-1">
            Las Revelaciones de {nombre}
          </h1>
          <p className="text-white/40 font-garamond text-lg mt-1">
            Tu mapa védico · Tradición Jyotish
          </p>
          <div className="gold-divider mt-6" />
        </div>

        {/* Cards */}
        <div className="space-y-5">
          {CARD_META.map((meta, i) => {
            const rev = revs[i]
            if (!rev) return null
            const isActive = streaming && i === revs.length - 1
            return (
              <RevCard
                key={i}
                rev={rev}
                meta={meta}
                isActive={isActive}
                delay={i === 0 ? 80 : 0}
              />
            )
          })}
        </div>

        {/* CTA — solo cuando termina el stream */}
        <div
          className={`mt-14 text-center transition-all duration-700 ${
            ctaVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
          }`}
        >
          <div className="gold-divider mb-8" />

          <p className="text-white/55 font-garamond text-xl leading-relaxed mb-2">
            Estas son solo 4 de las decenas de revelaciones que tu carta tiene.
          </p>
          <p className="text-white/35 font-garamond text-base mb-8">
            Dario Jiménez Medina puede leer tu carta completa en profundidad.
          </p>

          <button
            onClick={onCTA}
            className="btn-gold px-10 py-4 rounded-full text-sm tracking-[0.22em] shadow-[0_4px_32px_rgba(212,175,55,0.22)]"
          >
            Quiero mi Lectura Completa &nbsp;✦
          </button>

          <p className="mt-5 text-white/25 text-sm font-garamond">
            Con audio de Dario · Informe Word · Tradición Jyotish desde Colombia
          </p>

          <div className="mt-6 flex items-center justify-center gap-3 text-white/20 text-xs font-garamond">
            <span>🙏 Más de 30 lecturas entregadas</span>
            <span>·</span>
            <span>Dario Jiménez Medina — Jyotish</span>
          </div>
        </div>

      </div>
    </div>
  )
}
