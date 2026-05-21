'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Components } from 'react-markdown'

export type BloqueEstado = 'pendiente' | 'generando' | 'completo'

interface Props {
  num: number
  titulo: string
  texto: string
  estado: BloqueEstado
}

interface ChapterMeta {
  roman: string
  symbol: string
  tagline: string
  border: string
  headerText: string
  divider: string
  glow: string
  dot: string
}

const CHAPTER_META: Record<number, ChapterMeta> = {
  1: {
    roman: 'I',
    symbol: '◉',
    tagline: 'Tu identidad en el cosmos · El mapa del alma',
    border: 'border-gold-DEFAULT/25',
    headerText: 'text-gold-DEFAULT',
    divider: 'bg-gold-DEFAULT/15',
    glow: 'rgba(212,175,55,0.05)',
    dot: 'bg-gold-DEFAULT',
  },
  2: {
    roman: 'II',
    symbol: '☽',
    tagline: 'El símbolo que te define · Tu naturaleza profunda',
    border: 'border-violet-500/25',
    headerText: 'text-violet-400',
    divider: 'bg-violet-500/15',
    glow: 'rgba(139,92,246,0.05)',
    dot: 'bg-violet-400',
  },
  3: {
    roman: 'III',
    symbol: '✦',
    tagline: 'Las mansiones lunares · Tu sistema de conciencia',
    border: 'border-cyan-500/20',
    headerText: 'text-cyan-400',
    divider: 'bg-cyan-500/12',
    glow: 'rgba(34,211,238,0.04)',
    dot: 'bg-cyan-400',
  },
  4: {
    roman: 'IV',
    symbol: '⚡',
    tagline: 'Las fuerzas cósmicas · Los deseos del alma',
    border: 'border-amber-500/25',
    headerText: 'text-amber-400',
    divider: 'bg-amber-500/15',
    glow: 'rgba(245,158,11,0.05)',
    dot: 'bg-amber-400',
  },
  5: {
    roman: 'V',
    symbol: '◈',
    tagline: 'Las dimensiones de tu vida · Tu mapa de ruta',
    border: 'border-rose-500/20',
    headerText: 'text-rose-400',
    divider: 'bg-rose-500/12',
    glow: 'rgba(244,63,94,0.04)',
    dot: 'bg-rose-400',
  },
}

const MD_COMPONENTS: Components = {
  h1: ({ children }) => (
    <h1 className="font-cinzel text-2xl text-gold-DEFAULT mt-10 mb-4 leading-snug">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="font-cinzel text-xl text-gold-DEFAULT mt-8 mb-3 leading-snug">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="font-cinzel text-sm text-gold-DEFAULT/75 mt-6 mb-2 tracking-wide uppercase">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="font-garamond text-[1.08rem] text-white/80 mb-4 leading-[1.8]">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="text-gold-DEFAULT/90 font-semibold">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="text-white/60 italic">{children}</em>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-gold-DEFAULT/35 pl-5 my-6 italic text-white/55 font-garamond text-[1.05rem] leading-relaxed">
      {children}
    </blockquote>
  ),
  hr: () => <div className="gold-divider my-8" />,
  ul: ({ children }) => <ul className="space-y-2.5 mb-5 pl-1">{children}</ul>,
  ol: ({ children }) => (
    <ol className="space-y-2.5 mb-5 list-decimal list-inside font-garamond text-white/80">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="flex items-start gap-2.5 font-garamond text-white/75 text-[1.05rem] leading-[1.75]">
      <span className="text-gold-DEFAULT/50 mt-1.5 text-xs flex-shrink-0">✦</span>
      <span>{children}</span>
    </li>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto mb-6 rounded-xl border border-gold-DEFAULT/12">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-white/[0.03]">{children}</thead>,
  th: ({ children }) => (
    <th className="text-left py-3 px-4 text-gold-DEFAULT/65 font-cinzel text-[10px] tracking-widest border-b border-gold-DEFAULT/15">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="py-2.5 px-4 text-white/70 border-b border-white/[0.04] font-garamond text-base leading-snug">
      {children}
    </td>
  ),
}

function Cursor() {
  return (
    <span
      className="inline-block w-0.5 h-[1.1em] bg-gold-DEFAULT/60 ml-0.5 align-middle animate-pulse"
      aria-hidden="true"
    />
  )
}

export default function BloqueCard({ num, titulo, texto, estado }: Props) {
  const meta = CHAPTER_META[num] ?? CHAPTER_META[1]
  const isPending = estado === 'pendiente'
  const isGenerando = estado === 'generando'
  const isCompleto = estado === 'completo'

  return (
    <div
      id={`bloque-${num}`}
      className={`mystic-card rounded-2xl border ${meta.border} mb-10 overflow-hidden transition-all duration-700 ${
        isPending ? 'opacity-40' : 'opacity-100'
      }`}
      style={{
        boxShadow: isPending ? 'none' : `inset 0 0 80px ${meta.glow}`,
      }}
    >
      {/* Chapter header */}
      <div className="px-8 md:px-10 pt-8 pb-6">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <p
              className={`font-cinzel text-[9px] tracking-[0.55em] uppercase mb-2 transition-colors ${
                isPending ? 'text-white/18' : `${meta.headerText} opacity-50`
              }`}
            >
              Capítulo {meta.roman}
            </p>
            <h2
              className={`font-cinzel text-xl md:text-2xl tracking-wide leading-snug transition-colors ${
                isPending ? 'text-white/22' : 'text-white/92'
              }`}
            >
              {titulo}
            </h2>
            <p
              className={`font-garamond text-sm mt-1.5 transition-colors ${
                isPending ? 'text-white/12' : 'text-white/30'
              }`}
            >
              {meta.tagline}
            </p>
          </div>

          <div className="flex-shrink-0 pt-0.5">
            {isPending && (
              <span className="font-cinzel text-[9px] tracking-[0.3em] text-white/18 uppercase">
                En espera
              </span>
            )}
            {isGenerando && (
              <span
                className={`font-cinzel text-[9px] tracking-[0.3em] uppercase animate-pulse ${meta.headerText}`}
              >
                Revelando ✦
              </span>
            )}
            {isCompleto && (
              <span
                className={`font-cinzel text-[9px] tracking-[0.35em] uppercase ${meta.headerText} opacity-45`}
              >
                ✦ Completo
              </span>
            )}
          </div>
        </div>

        {/* Divider */}
        <div className={`mt-5 h-px ${isPending ? 'bg-white/5' : meta.divider}`} />
      </div>

      {/* Chapter content */}
      <div className="px-8 md:px-12 pb-10">
        {isPending && (
          <div className="space-y-3 select-none">
            {[74, 100, 88, 60, 94, 70].map((w, i) => (
              <div
                key={i}
                className="h-3 bg-white/[0.03] rounded"
                style={{ width: `${w}%` }}
              />
            ))}
          </div>
        )}

        {isGenerando && (
          <div className="font-garamond text-[1.08rem] text-white/78 leading-[1.8] whitespace-pre-wrap">
            {texto}
            <Cursor />
          </div>
        )}

        {isCompleto && texto && (
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
            {texto}
          </ReactMarkdown>
        )}
      </div>
    </div>
  )
}
