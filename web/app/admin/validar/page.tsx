'use client'

import { useState, useEffect } from 'react'
import AdminNav from '@/components/AdminNav'
import { createClient } from '@/lib/supabase/client'

// ─── Types ────────────────────────────────────────────────────────────────────

interface PlanetEntry {
  planeta: string; signo: string; signo_idx: number; grado: string
  deg_en_signo: number; casa: number; retrograde: boolean
  dignidad: string; nakshatra: string; pada: number
}
interface D1 {
  lagna: { signo: string; signo_idx: number; grado: string; deg_en_signo: number }
  planetas: PlanetEntry[]
}
interface ShadbalaRow {
  planeta: string; uccha_bala: number; saptavargaja: number; kendradi: number
  dig_bala: number; chesta_bala: number; naisargika: number
  total_shashtiamsas: number; rupas: number; minimo_rupas: number
  pct_minimo: number; rango: number; ishta_phala: number; kashta_phala: number
}
interface BhavaRow {
  casa: number; cusp: string; cusp_lon: number; signo: string; lord: string; sandhi: string
}
interface KarakaDetalle {
  karaka: string; abr: string; planeta: string; signo: string; deg_en_signo: number
}
interface BirthData {
  nombre: string
  nacimiento: { fecha: string; hora: string; ciudad: string; ayanamsa_lahiri: number }
  d1: D1
  shad_bala: ShadbalaRow[]
  karakas_jaimini: Record<string, string>
  karakas_jaimini_detalle: KarakaDetalle[]
  karakamsha: { planeta_ak: string; signo: string }
  upapada_lagna: { signo: string; lord_casa12: string }
  bhava_sripati: BhavaRow[]
}

// ─── Constants ────────────────────────────────────────────────────────────────

const API_URL = (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) || 'http://localhost:8000'

const PLANET_SHORT: Record<string, string> = {
  'Sol': 'Su', 'Luna': 'Mo', 'Marte': 'Ma', 'Mercurio': 'Me',
  'Júpiter': 'Ju', 'Venus': 'Ve', 'Saturno': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke',
}

const SIGN_ABBR = ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Acu','Pis']

// South Indian layout: row × col → sign index (0=Aries … 11=Pisces), -1=center
const SOUTH_LAYOUT = [
  [11,  0,  1,  2],
  [10, -1, -1,  3],
  [ 9, -1, -1,  4],
  [ 8,  7,  6,  5],
]

const KARAKA_ABBR: Record<string, string> = {
  'Atmakaraka (AK)': 'AK', 'Amatyakaraka (AMK)': 'AMK',
  'Bhratrikaraka (BK)': 'BK', 'Matrikaraka (MK)': 'MK',
  'Putrakaraka (PK)': 'PK', 'Gnatikaraka (GK)': 'GK', 'Darakaraka (DK)': 'DK',
}

// ─── D-1 South Indian Chart ───────────────────────────────────────────────────

function D1Chart({ d1 }: { d1: D1 }) {
  const lagnaSign = d1.lagna.signo_idx

  const signMap: Record<number, PlanetEntry[]> = {}
  for (let i = 0; i < 12; i++) signMap[i] = []
  for (const p of d1.planetas) {
    if (p.planeta !== 'Lagna') signMap[p.signo_idx]?.push(p)
  }

  function Cell({ si }: { si: number }) {
    const isLagna = si === lagnaSign
    const planets = signMap[si] || []
    return (
      <td
        className={`border align-top p-1.5 ${isLagna
          ? 'border-gold-DEFAULT/40 bg-gold-DEFAULT/[0.06]'
          : 'border-white/10 bg-white/[0.015]'
        }`}
        style={{ width: '25%', minHeight: 72, verticalAlign: 'top' }}
      >
        <div className="flex justify-between items-start mb-0.5">
          <span className={`font-cinzel text-[8px] tracking-wider ${isLagna ? 'text-gold-DEFAULT' : 'text-white/28'}`}>
            {SIGN_ABBR[si]}
          </span>
          <span className="font-cinzel text-[7px] text-white/18">{si + 1}</span>
        </div>
        {isLagna && (
          <div className="font-garamond text-[10px] text-gold-DEFAULT/75 leading-tight mb-0.5">
            Lg {d1.lagna.deg_en_signo.toFixed(1)}°
          </div>
        )}
        {planets.map(p => (
          <div key={p.planeta} className="font-garamond text-[10px] text-white/65 leading-tight">
            {PLANET_SHORT[p.planeta] ?? p.planeta.slice(0, 2)}
            {p.retrograde ? <span className="text-amber-400/60">℞</span> : ''}{' '}
            {p.deg_en_signo.toFixed(1)}°
          </div>
        ))}
      </td>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-white/10">
      <table className="w-full border-collapse" style={{ tableLayout: 'fixed' }}>
        <tbody>
          {SOUTH_LAYOUT.map((row, ri) => (
            <tr key={ri}>
              {row.map((si, ci) => {
                if (si === -1) return null
                if (ri === 1 && ci === 1) {
                  return (
                    <td
                      key="ctr"
                      colSpan={2}
                      rowSpan={2}
                      className="border border-white/10 bg-mystic-800/60 text-center"
                      style={{ verticalAlign: 'middle' }}
                    >
                      <p className="font-cinzel text-[8px] tracking-[0.3em] text-gold-DEFAULT/22 uppercase">Carta</p>
                      <p className="font-cinzel text-[11px] tracking-[0.4em] text-gold-DEFAULT/38 uppercase">Natal</p>
                      <p className="font-cinzel text-[7px] tracking-[0.3em] text-white/15 uppercase mt-1">D · 1</p>
                    </td>
                  )
                }
                return <Cell key={ci} si={si} />
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Planet Table ─────────────────────────────────────────────────────────────

function PlanetTable({ d1 }: { d1: D1 }) {
  const TH = 'font-cinzel text-[8px] tracking-[0.2em] text-white/28 uppercase px-3 py-2 text-right whitespace-nowrap'
  const TD = 'font-garamond text-sm text-white/65 px-3 py-2'
  const planets = d1.planetas.filter(p => p.planeta !== 'Lagna')

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/8">
            <th className={TH + ' text-left'}>Planeta</th>
            <th className={TH + ' text-left'}>Signo</th>
            <th className={TH}>Grado</th>
            <th className={TH}>Casa</th>
            <th className={TH + ' text-left'}>Nakshatra</th>
            <th className={TH}>Pada</th>
            <th className={TH + ' text-left'}>Dignidad</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b border-white/[0.04] bg-gold-DEFAULT/[0.025]">
            <td className={TD + ' text-gold-DEFAULT/75'}>Lagna (Asc)</td>
            <td className={TD + ' text-white/80'}>{d1.lagna.signo}</td>
            <td className={TD + ' text-right font-mono text-xs'}>{d1.lagna.grado.split(' ')[0]}</td>
            <td className={TD + ' text-right'}>1</td>
            <td className={TD} colSpan={3} />
          </tr>
          {planets.map((p, i) => (
            <tr key={p.planeta} className={`border-b border-white/[0.04] ${i % 2 === 0 ? '' : 'bg-white/[0.015]'}`}>
              <td className={TD + ' text-left'}>
                <span className="text-white/85">{p.planeta}</span>
                {p.retrograde && <span className="ml-1 text-amber-400/60 text-xs">℞</span>}
              </td>
              <td className={TD}>{p.signo}</td>
              <td className={TD + ' text-right font-mono text-xs'}>{p.grado.split(' ')[0]}</td>
              <td className={TD + ' text-right'}>{p.casa}</td>
              <td className={TD}>{p.nakshatra}</td>
              <td className={TD + ' text-right'}>{p.pada}</td>
              <td className={TD}>
                <span className={
                  p.dignidad === 'Exaltado'     ? 'text-gold-DEFAULT' :
                  p.dignidad === 'Propio'       ? 'text-cyan-400/80' :
                  p.dignidad === 'Moolatrikona' ? 'text-violet-400/80' :
                  p.dignidad === 'Débil'        ? 'text-red-400/60' :
                  'text-white/25'
                }>
                  {p.dignidad}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Shadbala Table ───────────────────────────────────────────────────────────

function ShadbalaTable({ data }: { data: ShadbalaRow[] }) {
  const TH = 'font-cinzel text-[7px] tracking-[0.18em] text-white/25 uppercase px-2 py-2 text-right whitespace-nowrap'
  const TD = 'font-garamond text-xs text-white/60 px-2 py-2 text-right tabular-nums'

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/8">
            <th className={TH + ' text-left'}>Planeta</th>
            <th className={TH}>Uccha</th>
            <th className={TH}>Saptav.</th>
            <th className={TH}>Kendradi</th>
            <th className={TH}>Dig</th>
            <th className={TH}>Chesta</th>
            <th className={TH}>Naisarg.</th>
            <th className={TH}>Total Sha.</th>
            <th className={TH}>Rupas</th>
            <th className={TH}>Mín.</th>
            <th className={TH}>% Mín.</th>
            <th className={TH}>Rango</th>
            <th className={TH}>Ishta</th>
            <th className={TH}>Kashta</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={row.planeta} className={`border-b border-white/[0.04] ${i % 2 === 0 ? '' : 'bg-white/[0.015]'}`}>
              <td className={TD + ' text-left text-white/80'}>{row.planeta}</td>
              <td className={TD}>{row.uccha_bala.toFixed(1)}</td>
              <td className={TD}>{row.saptavargaja.toFixed(1)}</td>
              <td className={TD}>{row.kendradi.toFixed(1)}</td>
              <td className={TD}>{row.dig_bala.toFixed(1)}</td>
              <td className={TD}>{row.chesta_bala.toFixed(1)}</td>
              <td className={TD}>{row.naisargika.toFixed(2)}</td>
              <td className={TD + ' text-white/75'}>{row.total_shashtiamsas.toFixed(2)}</td>
              <td className={TD + ' text-white/80 font-cinzel text-[11px]'}>{row.rupas.toFixed(3)}</td>
              <td className={TD + ' text-white/38'}>{row.minimo_rupas.toFixed(1)}</td>
              <td className={TD}>
                <span className={
                  row.pct_minimo >= 100 ? 'text-emerald-400/80' :
                  row.pct_minimo >= 75  ? 'text-amber-400/70' :
                  'text-red-400/65'
                }>
                  {row.pct_minimo.toFixed(1)}%
                </span>
              </td>
              <td className={TD}>
                <span className="font-cinzel text-[12px] text-white/70">{row.rango}</span>
              </td>
              <td className={TD}>{row.ishta_phala.toFixed(2)}</td>
              <td className={TD}>{row.kashta_phala.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Jaimini Table ────────────────────────────────────────────────────────────

function JaiminiTable({ detalle, karakamsha, upapada }: {
  detalle: KarakaDetalle[]
  karakamsha: { planeta_ak: string; signo: string }
  upapada: { signo: string; lord_casa12: string }
}) {
  const TH = 'font-cinzel text-[8px] tracking-[0.2em] text-white/28 uppercase px-3 py-2 text-left'
  const TD = 'font-garamond text-sm px-3 py-2'

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Karakas */}
      <div>
        <p className="font-cinzel text-[9px] tracking-[0.4em] text-white/22 uppercase mb-3">Chara Karakas</p>
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/8">
              <th className={TH}>Karaka</th>
              <th className={TH}>Abr.</th>
              <th className={TH}>Planeta</th>
              <th className={TH + ' text-right'}>Signo</th>
              <th className={TH + ' text-right'}>Grado</th>
            </tr>
          </thead>
          <tbody>
            {detalle.map((row, i) => (
              <tr key={row.karaka} className={`border-b border-white/[0.04] ${i % 2 === 0 ? '' : 'bg-white/[0.015]'}`}>
                <td className={TD + ' text-white/40 text-xs'}>{row.karaka.split('(')[0].trim()}</td>
                <td className={TD + ' font-cinzel text-[10px] text-gold-DEFAULT/55'}>{row.abr}</td>
                <td className={TD + ' text-white/80'}>{row.planeta}</td>
                <td className={TD + ' text-right text-white/45 text-xs'}>{row.signo}</td>
                <td className={TD + ' text-right font-mono text-xs text-white/55'}>{row.deg_en_signo.toFixed(2)}°</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Karakamsha + Upapada */}
      <div className="space-y-4">
        <div className="mystic-card rounded-xl border border-gold-DEFAULT/15 p-5">
          <p className="font-cinzel text-[8px] tracking-[0.45em] text-gold-DEFAULT/30 uppercase mb-2">Karakamsha</p>
          <p className="font-garamond text-white/35 text-sm mb-2">Navamsha del Atmakaraka</p>
          <p className="font-cinzel text-xl text-gold-DEFAULT/75">{karakamsha.signo}</p>
          <p className="font-garamond text-xs text-white/25 mt-1">AK: {karakamsha.planeta_ak}</p>
        </div>
        <div className="mystic-card rounded-xl border border-violet-500/15 p-5">
          <p className="font-cinzel text-[8px] tracking-[0.45em] text-violet-400/30 uppercase mb-2">Upapada Lagna</p>
          <p className="font-garamond text-white/35 text-sm mb-2">Arudha Pada · Casa 12</p>
          <p className="font-cinzel text-xl text-violet-400/75">{upapada.signo}</p>
          <p className="font-garamond text-xs text-white/25 mt-1">Lord Casa 12: {upapada.lord_casa12}</p>
        </div>
      </div>
    </div>
  )
}

// ─── House Cusp Table ─────────────────────────────────────────────────────────

function HouseCuspTable({ bhava }: { bhava: BhavaRow[] }) {
  const TH = 'font-cinzel text-[8px] tracking-[0.2em] text-white/28 uppercase px-3 py-2'
  const TD = 'font-garamond text-sm px-3 py-2'

  const KENDRA   = new Set([1, 4, 7, 10])
  const TRIKONA  = new Set([1, 5, 9])
  const DUSTHANA = new Set([6, 8, 12])

  function houseColor(n: number) {
    if (KENDRA.has(n) && TRIKONA.has(n)) return 'text-gold-DEFAULT'
    if (KENDRA.has(n))   return 'text-cyan-400/80'
    if (TRIKONA.has(n))  return 'text-emerald-400/80'
    if (DUSTHANA.has(n)) return 'text-red-400/50'
    return 'text-white/65'
  }

  function houseTag(n: number) {
    if (KENDRA.has(n) && TRIKONA.has(n)) return <span className="text-[7px] text-gold-DEFAULT/40 font-cinzel ml-1">K+T</span>
    if (KENDRA.has(n))   return <span className="text-[7px] text-cyan-400/35 font-cinzel ml-1">Kend</span>
    if (TRIKONA.has(n))  return <span className="text-[7px] text-emerald-400/35 font-cinzel ml-1">Trik</span>
    if (DUSTHANA.has(n)) return <span className="text-[7px] text-red-400/35 font-cinzel ml-1">Dust</span>
    return null
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/8">
            <th className={TH + ' text-left'}>Casa</th>
            <th className={TH + ' text-left'}>Signo</th>
            <th className={TH + ' text-right'}>Bhava Madhya</th>
            <th className={TH + ' text-left'}>Lord</th>
            <th className={TH + ' text-right'}>Sandhi</th>
          </tr>
        </thead>
        <tbody>
          {bhava.map((row, i) => (
            <tr key={row.casa} className={`border-b border-white/[0.04] ${i % 2 === 0 ? '' : 'bg-white/[0.015]'}`}>
              <td className={TD + ' text-left'}>
                <span className={`font-cinzel text-sm ${houseColor(row.casa)}`}>{row.casa}</span>
                {houseTag(row.casa)}
              </td>
              <td className={TD + ' text-white/75'}>{row.signo}</td>
              <td className={TD + ' text-right font-mono text-xs text-white/55'}>{row.cusp}</td>
              <td className={TD + ' text-white/70'}>{row.lord}</td>
              <td className={TD + ' text-right font-mono text-xs text-white/38'}>{row.sandhi}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Section Wrapper ──────────────────────────────────────────────────────────

function Section({ roman, title, tagline, children }: {
  roman: string; title: string; tagline: string; children: React.ReactNode
}) {
  return (
    <div className="mystic-card rounded-2xl border border-white/8 overflow-hidden mb-8">
      <div className="border-b border-white/8 px-6 py-4 flex items-center gap-4 bg-white/[0.01]">
        <span className="font-cinzel text-3xl text-gold-DEFAULT/22 shrink-0">{roman}</span>
        <div>
          <p className="font-cinzel text-[11px] tracking-[0.25em] text-white/75 uppercase">{title}</p>
          <p className="font-garamond text-white/28 text-sm">{tagline}</p>
        </div>
      </div>
      <div className="p-6">{children}</div>
    </div>
  )
}

// ─── Input style ──────────────────────────────────────────────────────────────

const INPUT = 'w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-white font-garamond text-base placeholder-white/18 focus:border-gold-DEFAULT/35 outline-none transition-colors'
const LABEL = 'block font-cinzel text-[9px] tracking-[0.35em] text-white/28 uppercase mb-1.5'

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function ValidarPage() {
  const [userEmail, setUserEmail] = useState('')
  const [nombre,    setNombre]    = useState('')
  const [fecha,     setFecha]     = useState('')
  const [hora,      setHora]      = useState('')
  const [ciudad,    setCiudad]    = useState('')
  const [loading,   setLoading]   = useState(false)
  const [data,      setData]      = useState<BirthData | null>(null)
  const [error,     setError]     = useState<string | null>(null)

  useEffect(() => {
    const supabase = createClient()
    void supabase.auth.getUser().then(res => setUserEmail(res.data.user?.email ?? ''))
  }, [])

  const formValid = nombre.trim() && fecha && hora && ciudad.trim()

  const handleCalcular = async () => {
    if (!formValid) return
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const resp = await fetch(`${API_URL}/api/birth-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, fecha, hora, ciudad }),
      })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error((err as { detail?: string }).detail ?? `Error ${resp.status}`)
      }
      setData(await resp.json() as BirthData)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen">
      <div className="stars-bg" aria-hidden="true" />
      <AdminNav userEmail={userEmail} />

      <div className="relative z-10 max-w-5xl mx-auto px-4 py-10">

        {/* Header */}
        <div className="mb-8">
          <p className="font-cinzel text-[10px] tracking-[0.5em] text-gold-DEFAULT/38 uppercase mb-1">
            Gráficas Védicas · Validación
          </p>
          <p className="font-garamond text-white/28 text-sm">
            Ingresa los datos natales y compara las 4 gráficas con Parashara&apos;s Light
          </p>
        </div>

        {/* Form */}
        <div className="mystic-card rounded-2xl border border-white/10 p-6 mb-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
            <div>
              <label className={LABEL}>Nombre</label>
              <input type="text" placeholder="Nombre completo" value={nombre}
                onChange={e => setNombre(e.target.value)} className={INPUT} />
            </div>
            <div>
              <label className={LABEL}>Fecha</label>
              <input type="date" value={fecha}
                onChange={e => setFecha(e.target.value)} className={INPUT} />
            </div>
            <div>
              <label className={LABEL}>Hora</label>
              <input type="time" value={hora}
                onChange={e => setHora(e.target.value)} className={INPUT} />
            </div>
            <div>
              <label className={LABEL}>Ciudad</label>
              <input type="text" placeholder="Ciudad, País" value={ciudad}
                onChange={e => setCiudad(e.target.value)} className={INPUT} />
            </div>
          </div>
          <button
            onClick={handleCalcular}
            disabled={!formValid || loading}
            className="btn-gold px-8 py-3 rounded-xl text-xs tracking-[0.22em] disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {loading ? 'Calculando…' : 'Calcular Cartas  ✦'}
          </button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block w-8 h-8 border-2 border-gold-DEFAULT/30 border-t-gold-DEFAULT rounded-full animate-spin mb-4" />
            <p className="font-garamond text-white/30 text-base">Calculando posiciones planetarias…</p>
            <p className="font-garamond text-white/18 text-sm mt-1">Esto puede tomar unos segundos</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mystic-card rounded-xl border border-red-400/20 p-5 mb-8">
            <p className="font-garamond text-red-400/70 text-base">{error}</p>
          </div>
        )}

        {/* Charts */}
        {data && (
          <>
            {/* Ayanamsa info */}
            <div className="flex items-center gap-6 mb-6 px-1">
              <p className="font-cinzel text-[9px] tracking-[0.4em] text-gold-DEFAULT/50 uppercase">
                {data.nombre}
              </p>
              <span className="font-garamond text-white/25 text-sm">
                {data.nacimiento.fecha} · {data.nacimiento.hora} · {data.nacimiento.ciudad}
              </span>
              <span className="font-garamond text-white/18 text-xs ml-auto">
                Ayanamsa Lahiri: {data.nacimiento.ayanamsa_lahiri.toFixed(4)}°
              </span>
            </div>

            {/* I — Carta Natal D-1 */}
            <Section roman="I" title="Carta Natal D-1" tagline="Birth Chart completo · Grados exactos · Nakshatras · Dignidades">
              <div className="grid md:grid-cols-2 gap-6">
                <D1Chart d1={data.d1} />
                <PlanetTable d1={data.d1} />
              </div>
            </Section>

            {/* II — Shadbala */}
            <Section roman="II" title="Shadbala" tagline="Rupas · % del mínimo · Ishta/Kashta Phala · Rangos">
              <ShadbalaTable data={data.shad_bala} />
              <div className="mt-4 flex gap-6 text-xs font-garamond text-white/25">
                <span><span className="text-emerald-400/70">■</span> ≥ 100% del mínimo</span>
                <span><span className="text-amber-400/60">■</span> 75–99%</span>
                <span><span className="text-red-400/55">■</span> &lt; 75%</span>
              </div>
            </Section>

            {/* III — Sistema Jaimini */}
            <Section roman="III" title="Sistema Jaimini" tagline="Chara Karakas · Karakamsha · Upapada Lagna">
              <JaiminiTable
                detalle={data.karakas_jaimini_detalle}
                karakamsha={data.karakamsha}
                upapada={data.upapada_lagna}
              />
            </Section>

            {/* IV — House Cusp Details */}
            <Section roman="IV" title="House Cusp Details" tagline="Bhava Madhya · Lord · Sandhi · Sistema Sripati/Porphyry">
              <HouseCuspTable bhava={data.bhava_sripati} />
              <p className="font-garamond text-white/15 text-xs mt-4">
                Nota: Cusps calculados con sistema Porphyry (aproximación Sripati). Para exactitud total se requiere pyswisseph.
              </p>
            </Section>
          </>
        )}
      </div>
    </div>
  )
}
