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

const BLOCK_COLORS: Record<number, string> = {
  1: 'border-gold-DEFAULT/40',
  2: 'border-violet-500/40',
  3: 'border-cyan-500/40',
  4: 'border-amber-500/40',
  5: 'border-rose-500/40',
}

const BLOCK_ACCENT: Record<number, string> = {
  1: 'text-gold-DEFAULT',
  2: 'text-violet-400',
  3: 'text-cyan-400',
  4: 'text-amber-400',
  5: 'text-rose-400',
}

const BLOCK_DOT: Record<number, string> = {
  1: 'bg-gold-DEFAULT',
  2: 'bg-violet-400',
  3: 'bg-cyan-400',
  4: 'bg-amber-400',
  5: 'bg-rose-400',
}

const MD_COMPONENTS: Components = {
  h1: ({ children }) => (
    <h1 className="font-cinzel text-2xl text-gold-DEFAULT mt-10 mb-4 leading-snug">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="font-cinzel text-xl text-gold-DEFAULT mt-8 mb-3 leading-snug">{children}</h2>
  ),
  h3: ({ children }) => (
    <h3 className="font-cinzel text-base text-gold-DEFAULT/80 mt-6 mb-2 tracking-wide">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="font-garamond text-lg text-white/80 mb-4 leading-relaxed">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="text-gold-DEFAULT font-semibold">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="text-white/65 italic">{children}</em>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-gold-DEFAULT/40 pl-5 my-5 italic text-white/60 font-garamond text-lg">
      {children}
    </blockquote>
  ),
  hr: () => <div className="gold-divider my-8" />,
  ul: ({ children }) => <ul className="space-y-2 mb-5 pl-1">{children}</ul>,
  ol: ({ children }) => (
    <ol className="space-y-2 mb-5 list-decimal list-inside font-garamond text-white/80">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="flex items-start gap-2 font-garamond text-white/75 text-base leading-relaxed">
      <span className="text-gold-DEFAULT/60 mt-1.5 text-xs flex-shrink-0">✦</span>
      <span>{children}</span>
    </li>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto mb-6 rounded-xl border border-gold-DEFAULT/15">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-white/[0.04]">{children}</thead>,
  th: ({ children }) => (
    <th className="text-left py-2.5 px-4 text-gold-DEFAULT/70 font-cinzel text-[11px] tracking-widest border-b border-gold-DEFAULT/20">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="py-2.5 px-4 text-white/70 border-b border-white/[0.05] font-garamond text-base leading-snug">
      {children}
    </td>
  ),
}

function Cursor() {
  return (
    <span
      className="inline-block w-0.5 h-5 bg-gold-DEFAULT ml-0.5 align-middle"
      style={{ animation: 'blink 1s step-end infinite' }}
    />
  )
}

export default function BloqueCard({ num, titulo, texto, estado }: Props) {
  const borderColor = BLOCK_COLORS[num] ?? 'border-gold-DEFAULT/40'
  const accentColor = BLOCK_ACCENT[num] ?? 'text-gold-DEFAULT'
  const dotColor = BLOCK_DOT[num] ?? 'bg-gold-DEFAULT'

  return (
    <div
      id={`bloque-${num}`}
      className={`mystic-card rounded-2xl border-l-4 ${borderColor} mb-8 overflow-hidden`}
    >
      {/* Block header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-white/[0.06]">
        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor} ${estado === 'generando' ? 'animate-pulse' : ''}`} />
        <span className="font-cinzel text-[10px] tracking-[0.35em] text-white/30 uppercase">
          Bloque {num} de 5
        </span>
        <span className={`font-cinzel text-sm ${accentColor} ml-1`}>{titulo}</span>
        {estado === 'completo' && (
          <span className="ml-auto text-[10px] tracking-widest text-white/25 font-cinzel">✦ Completo</span>
        )}
        {estado === 'generando' && (
          <span className="ml-auto text-[10px] tracking-widest text-gold-DEFAULT/50 font-cinzel animate-pulse">
            Generando...
          </span>
        )}
      </div>

      {/* Block body */}
      <div className="px-6 md:px-10 py-6">
        {estado === 'pendiente' && (
          <div className="space-y-3 opacity-20 select-none">
            <div className="h-4 bg-white/10 rounded w-3/4" />
            <div className="h-4 bg-white/10 rounded w-full" />
            <div className="h-4 bg-white/10 rounded w-5/6" />
          </div>
        )}

        {estado === 'generando' && (
          <div className="font-garamond text-lg text-white/75 leading-relaxed whitespace-pre-wrap">
            {texto}
            <Cursor />
          </div>
        )}

        {estado === 'completo' && texto && (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={MD_COMPONENTS}
          >
            {texto}
          </ReactMarkdown>
        )}
      </div>
    </div>
  )
}
