import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import AdminNav from '@/components/AdminNav'

const TIPO_LABEL: Record<string, string> = {
  carta: 'Carta Astral',
  predicciones: 'Predicciones',
  compatibilidad: 'Compatibilidad',
}

const TIPO_COLOR: Record<string, string> = {
  carta: 'text-gold-DEFAULT border-gold-DEFAULT/30 bg-gold-DEFAULT/8',
  predicciones: 'text-violet-400 border-violet-400/30 bg-violet-400/8',
  compatibilidad: 'text-rose-400 border-rose-400/30 bg-rose-400/8',
}

const ESTADO_COLOR: Record<string, string> = {
  completo: 'text-emerald-400/70',
  generando: 'text-gold-DEFAULT/70 animate-pulse',
  pendiente: 'text-white/25',
  error: 'text-red-400/70',
}

function formatFecha(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('es-CO', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
}

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/admin')

  const { data: lecturas } = await supabase
    .from('lecturas')
    .select('*, clientes(nombre)')
    .order('created_at', { ascending: false })
    .limit(50)

  return (
    <div className="relative min-h-screen">
      <div className="stars-bg" aria-hidden="true" />
      <AdminNav userEmail={user.email!} />

      <div className="relative z-10 max-w-5xl mx-auto px-4 py-10">

        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="font-cinzel text-2xl gold-text tracking-wide mb-1">
              Panel de Lecturas
            </h1>
            <p className="font-garamond text-white/35 text-base">
              {lecturas?.length ?? 0} lecturas guardadas
            </p>
          </div>
          <Link
            href="/admin/nueva"
            className="btn-gold px-7 py-3 rounded-xl text-xs tracking-[0.2em] shadow-[0_4px_24px_rgba(212,175,55,0.2)]"
          >
            + Nueva Lectura
          </Link>
        </div>

        {/* List */}
        {!lecturas || lecturas.length === 0 ? (
          <div className="mystic-card rounded-2xl border border-white/8 p-16 text-center">
            <div className="text-3xl mb-4 text-gold-DEFAULT/30 select-none">✦</div>
            <p className="font-cinzel text-white/25 text-sm tracking-wide">
              No hay lecturas todavía
            </p>
            <p className="font-garamond text-white/18 text-base mt-2">
              Crea la primera lectura con el botón de arriba.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {lecturas.map((l: Record<string, unknown>) => {
              const cliente = l.clientes as { nombre: string } | null
              const tipo = l.tipo as string
              const estado = l.estado as string
              return (
                <Link
                  key={l.id as string}
                  href={`/admin/lecturas/${l.id}`}
                  className="mystic-card mystic-card-hover rounded-xl border border-white/8 px-5 py-4 flex items-center gap-4 group transition-all"
                >
                  {/* Client name */}
                  <div className="flex-1 min-w-0">
                    <p className="font-cinzel text-white/85 text-sm group-hover:text-gold-DEFAULT/90 transition-colors truncate">
                      {cliente?.nombre ?? '—'}
                    </p>
                    <p className="font-garamond text-white/30 text-sm mt-0.5">
                      {formatFecha(l.created_at as string)}
                    </p>
                  </div>

                  {/* Tipo badge */}
                  <span className={`font-cinzel text-[9px] tracking-[0.3em] uppercase border rounded-full px-3 py-1 flex-shrink-0 ${TIPO_COLOR[tipo] ?? 'text-white/30 border-white/15'}`}>
                    {TIPO_LABEL[tipo] ?? tipo}
                  </span>

                  {/* Estado */}
                  <span className={`font-cinzel text-[9px] tracking-[0.25em] uppercase flex-shrink-0 ${ESTADO_COLOR[estado] ?? 'text-white/25'}`}>
                    {estado === 'completo' ? '✦ Completo' : estado}
                  </span>

                  {/* Arrow */}
                  <span className="text-white/15 group-hover:text-gold-DEFAULT/40 transition-colors flex-shrink-0 text-lg">
                    ›
                  </span>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
