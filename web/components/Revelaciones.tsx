'use client'

import { useEffect, useState } from 'react'
import type { RevStream } from '@/app/page'

type Tipo = 'individual' | 'pareja'

interface Props {
  nombre: string
  revs: RevStream[]
  streaming: boolean
  tipo: Tipo
  onCTA: () => void
  onBack?: () => void
}

const CARD_META_INDIVIDUAL = [
  {
    icon: '🌟',
    subtitle: 'Tu luz y tu sombra · Lo que el cosmos ve en ti',
    accent: 'border-gold-DEFAULT/30',
    glow: 'rgba(212,175,55,0.06)',
  },
  {
    icon: '⏳',
    subtitle: 'Tu ciclo y tu renacimiento · La danza del tiempo',
    accent: 'border-purple-500/25',
    glow: 'rgba(168,85,247,0.06)',
  },
]

const CARD_META_PAREJA = [
  {
    icon: '💫',
    subtitle: 'Lo que el cosmos ve en su unión · Kundali Matching',
    accent: 'border-rose-400/30',
    glow: 'rgba(244,63,94,0.06)',
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
  meta: { icon: string; subtitle: string; accent: string; glow: string }
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
          <h2 className="font-cinzel text-gold-DEFAULT text-lg tracking-wide leading-snug">
            {rev.titulo || <span className="opacity-0">…</span>}
          </h2>
          <p className="font-cinzel text-[9px] tracking-[0.38em] text-gold-DEFAULT/38 uppercase mb-4">
            {meta.subtitle}
          </p>
          <p className="text-white/82 font-garamond text-[1.08rem] leading-[1.75] whitespace-pre-wrap">
            {rev.cuerpo}
            {isActive && !hasPromesa && <Cursor />}
          </p>
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

export default function Revelaciones({ nombre, revs, streaming, tipo, onCTA, onBack }: Props) {
  const [ctaVisible, setCtaVisible] = useState(false)
  const expectedCount = tipo === 'pareja' ? 1 : 2
  const cardMeta = tipo === 'pareja' ? CARD_META_PAREJA : CARD_META_INDIVIDUAL

  useEffect(() => {
    if (!streaming && revs.length >= expectedCount) {
      const t = setTimeout(() => setCtaVisible(true), 900)
      return () => clearTimeout(t)
    }
  }, [streaming, revs.length, expectedCount])

  const headerTitle = tipo === 'pareja'
    ? `La Compatibilidad de ${nombre}`
    : `Las Revelaciones de ${nombre}`

  const ctaButton = tipo === 'pareja'
    ? 'Quiero el análisis completo de nuestra compatibilidad'
    : 'Quiero mi Lectura Completa'

  const ctaSubtitle = tipo === 'pareja'
    ? 'Análisis Kundali completo · 12 secciones · Dario Jiménez Medina'
    : 'Con audio de Dario · Informe completo · Tradición Jyotish'

  const ctaTeaser = tipo === 'pareja'
    ? 'Esta es solo una de las decenas de dimensiones que el cosmos tiene para su unión.'
    : 'Estas son solo 2 de las decenas de revelaciones que tu carta tiene.'

  return (
    <div className="min-h-screen px-4 py-16 relative z-10">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10 animate-fade-in">
          {onBack && (
            <button
              onClick={onBack}
              className="font-cinzel text-[11px] tracking-[0.3em] text-white/55 hover:text-gold-DEFAULT transition-colors mb-6 block mx-auto border border-white/15 hover:border-gold-DEFAULT/40 px-4 py-2 rounded-full"
            >
              ← Inicio
            </button>
          )}
          <div className="text-3xl mb-3 tracking-widest select-none"
            style={{ color: tipo === 'pareja' ? 'rgba(244,63,94,0.5)' : 'rgba(212,175,55,0.5)' }}>
            {tipo === 'pareja' ? '♡ · ✦ · ♡' : '☽ · ✦ · ☾'}
          </div>
          <h1 className="font-cinzel text-3xl md:text-4xl gold-text tracking-wide mb-1">
            {headerTitle}
          </h1>
          <p className="text-white/40 font-garamond text-lg mt-1">
            {tipo === 'pareja' ? 'Kundali Matching · Tradición Jyotish' : 'Tu mapa védico · Tradición Jyotish'}
          </p>
          <div className="gold-divider mt-6" />
        </div>

        {/* Cards */}
        <div className="space-y-5">
          {cardMeta.map((meta, i) => {
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

        {/* CTA */}
        <div
          className={`mt-14 text-center transition-all duration-700 ${
            ctaVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'
          }`}
        >
          <div className="gold-divider mb-8" />
          <p className="text-white/55 font-garamond text-xl leading-relaxed mb-2">
            {ctaTeaser}
          </p>
          <p className="text-white/35 font-garamond text-base mb-8">
            Dario Jiménez Medina puede{' '}
            {tipo === 'pareja' ? 'leer su compatibilidad completa en profundidad.' : 'leer tu carta completa en profundidad.'}
          </p>
          <button
            onClick={onCTA}
            className="btn-gold px-10 py-4 rounded-full text-sm tracking-[0.18em] shadow-[0_4px_32px_rgba(212,175,55,0.22)]"
          >
            {ctaButton} &nbsp;✦
          </button>
          <p className="mt-5 text-white/25 text-sm font-garamond">{ctaSubtitle}</p>
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
