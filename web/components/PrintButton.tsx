'use client'

export default function PrintButton() {
  return (
    <button
      onClick={() => window.print()}
      className="font-cinzel text-[10px] tracking-[0.3em] text-white/40 hover:text-gold-DEFAULT border border-white/10 hover:border-gold-DEFAULT/30 px-3 py-1.5 rounded-full transition-colors print:hidden"
    >
      Imprimir / PDF
    </button>
  )
}
