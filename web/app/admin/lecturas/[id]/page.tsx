import { createClient } from '@/lib/supabase/server'
import { redirect, notFound } from 'next/navigation'
import Link from 'next/link'
import BloqueCard from '@/components/BloqueCard'
import PrintButton from '@/components/PrintButton'

interface BloqueData {
  num: number
  titulo: string
  texto: string
}

const TIPO_LABEL: Record<string, string> = {
  carta: 'Carta Astral Védica',
  predicciones: 'Lectura de Predicciones',
  compatibilidad: 'Kundali Matching · Compatibilidad',
}

function formatFecha(iso: string) {
  try {
    const [y, m, d] = iso.split('-').map(Number)
    const meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto',
                   'septiembre','octubre','noviembre','diciembre']
    return `${d} de ${meses[m - 1]} de ${y}`
  } catch { return iso }
}

export default async function LecturaPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const supabase = await createClient()

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/admin')

  const { data: lectura } = await supabase
    .from('lecturas')
    .select('*, clientes(*)')
    .eq('id', id)
    .single()

  if (!lectura) notFound()

  const cliente = lectura.clientes as {
    nombre: string
    fecha_nacimiento: string
    hora_nacimiento: string
    ciudad: string
  } | null

  const bloques: BloqueData[] = Array.isArray(lectura.contenido) ? lectura.contenido : []
  const tipo: string = lectura.tipo

  const tituloDisplay =
    tipo === 'compatibilidad' && lectura.pareja_nombre
      ? `${cliente?.nombre ?? ''} y ${lectura.pareja_nombre}`
      : (cliente?.nombre ?? '—')

  return (
    <div className="relative min-h-screen">
      <div className="stars-bg" aria-hidden="true" />

      {/* Sticky nav */}
      <div className="sticky top-0 z-50 bg-mystic-900/95 backdrop-blur-md border-b border-white/[0.06] print:hidden">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-3">
          <Link
            href="/admin/dashboard"
            className="font-cinzel text-[10px] tracking-[0.3em] text-white/45 hover:text-gold-DEFAULT transition-colors border border-white/12 hover:border-gold-DEFAULT/35 px-3 py-1.5 rounded-full"
          >
            ← Historial
          </Link>

          <span className="font-cinzel text-[9px] tracking-[0.35em] text-gold-DEFAULT/30 uppercase flex-1 text-center truncate">
            {TIPO_LABEL[tipo] ?? tipo}
          </span>

          <PrintButton />

          <Link
            href="/admin/nueva"
            className="font-cinzel text-[10px] tracking-[0.25em] text-white/35 hover:text-gold-DEFAULT border border-white/10 hover:border-gold-DEFAULT/30 px-3 py-1.5 rounded-full transition-colors"
          >
            + Nueva
          </Link>
        </div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto px-4 py-12">

        {/* Cover */}
        <div className="text-center mb-14 print:mb-10">
          <div className="text-2xl mb-4 tracking-widest text-gold-DEFAULT/38 select-none">
            {tipo === 'compatibilidad' ? '♡ · ✦ · ♡' : '☽ · ✦ · ☾'}
          </div>
          <p className="font-cinzel text-[10px] tracking-[0.55em] text-gold-DEFAULT/35 uppercase mb-3">
            {TIPO_LABEL[tipo] ?? tipo} · Jyotish
          </p>
          <h1 className="font-cinzel text-4xl md:text-5xl gold-text tracking-wide mb-2">
            {tituloDisplay}
          </h1>
          {cliente && (
            <p className="font-garamond text-white/30 text-base">
              {formatFecha(cliente.fecha_nacimiento)}
              {cliente.hora_nacimiento && ` · ${cliente.hora_nacimiento.slice(0, 5)}`}
              {cliente.ciudad && ` · ${cliente.ciudad}`}
            </p>
          )}
          <div className="gold-divider mt-8 mb-6" />
          <div className="inline-flex items-center gap-2 bg-gold-DEFAULT/7 border border-gold-DEFAULT/18 rounded-full px-5 py-2">
            <span className="text-gold-DEFAULT text-xs">✦</span>
            <span className="font-cinzel text-[10px] tracking-[0.4em] text-gold-DEFAULT uppercase">
              Lectura Completa
            </span>
            <span className="text-gold-DEFAULT text-xs">✦</span>
          </div>
        </div>

        {/* Chapters */}
        {bloques.length === 0 ? (
          <div className="mystic-card rounded-2xl border border-white/8 p-12 text-center">
            <p className="font-garamond text-white/35 text-base">No hay contenido guardado para esta lectura.</p>
          </div>
        ) : (
          bloques.map((b) => (
            <BloqueCard
              key={b.num}
              num={b.num}
              titulo={b.titulo}
              texto={b.texto}
              estado="completo"
            />
          ))
        )}

        {/* Footer */}
        <div className="text-center mt-4 mb-16">
          <div className="gold-divider mb-8" />
          <div className="text-xl mb-3 tracking-widest text-gold-DEFAULT/25 select-none">☽ · ✦ · ☾</div>
          <p className="font-cinzel text-[9px] tracking-[0.5em] text-gold-DEFAULT/25 uppercase mb-2">
            Fin de la Lectura
          </p>
          <p className="font-garamond text-white/18 text-base">
            Dario Jiménez Medina · Jyotish · Bogotá, Colombia
          </p>
        </div>
      </div>
    </div>
  )
}
