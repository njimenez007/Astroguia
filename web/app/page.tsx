'use client'

import { useRef, useState } from 'react'
import LandingForm, { FormData } from '@/components/LandingForm'
import ParejaForm, { ParejaData } from '@/components/ParejaForm'
import LoadingScreen from '@/components/LoadingScreen'
import Revelaciones from '@/components/Revelaciones'
import Upsell from '@/components/Upsell'

type Tipo = 'individual' | 'pareja'
type Screen = 'selector' | 'form' | 'loading' | 'revelaciones' | 'upsell'

export interface RevStream {
  titulo: string
  cuerpo: string
  promesa: string
}

function parseRevBuffer(text: string): RevStream[] {
  const result: Array<RevStream | undefined> = [undefined, undefined, undefined, undefined]
  const parts = text.split(/(\[R[1-4][TCP]\])/)

  let curIdx = -1
  let curSection: 'titulo' | 'cuerpo' | 'promesa' | null = null

  for (const part of parts) {
    const m = part.match(/^\[R([1-4])([TCP])\]$/)
    if (m) {
      const idx = parseInt(m[1]) - 1
      const type = m[2]
      if (type === 'T') {
        result[idx] = { titulo: '', cuerpo: '', promesa: '' }
        curIdx = idx
        curSection = 'titulo'
      } else if (type === 'C') {
        curSection = 'cuerpo'
      } else if (type === 'P') {
        curSection = 'promesa'
      }
    } else if (curIdx >= 0 && curSection && part) {
      const rev = result[curIdx]!
      if (curSection === 'titulo') rev.titulo += part
      else if (curSection === 'cuerpo') rev.cuerpo += part
      else if (curSection === 'promesa') rev.promesa += part
    }
  }

  return result
    .filter((r): r is RevStream => r !== undefined)
    .map(r => ({
      titulo: r.titulo.replace(/^\n+/, '').trimEnd(),
      cuerpo: r.cuerpo.replace(/^\n+/, '').trimEnd(),
      promesa: r.promesa.replace(/^\n+/, '').trimEnd(),
    }))
}

const API_URL =
  (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) ||
  'http://localhost:8000'

export default function Home() {
  const [screen, setScreen] = useState<Screen>('selector')
  const [tipo, setTipo] = useState<Tipo>('individual')
  const [formData, setFormData] = useState<FormData | null>(null)
  const [parejaData, setParejaData] = useState<ParejaData | null>(null)
  const [revs, setRevs] = useState<RevStream[]>([])
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const transitionedRef = useRef(false)

  const loadingNombre =
    tipo === 'pareja' && parejaData
      ? `${parejaData.nombre} y ${parejaData.pareja_nombre}`
      : formData?.nombre ?? ''

  const revelacionNombre =
    tipo === 'pareja' ? (parejaData?.nombre ?? '') : (formData?.nombre ?? '')

  const runStream = async (body: object) => {
    setError(null)
    setRevs([])
    setStreaming(true)
    transitionedRef.current = false
    setScreen('loading')

    try {
      const resp = await fetch(`${API_URL}/api/gancho`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!resp.ok) {
        const detail = await resp.text()
        throw new Error(`Error ${resp.status}: ${detail}`)
      }

      const reader = resp.body!.getReader()
      const decoder = new TextDecoder()
      let remainder = ''
      let accumulated = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const raw = decoder.decode(value, { stream: true })
        const text = remainder + raw
        const lines = text.split('\n')
        remainder = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          let payload: { e: string; t?: string; m?: string }
          try {
            payload = JSON.parse(line.slice(6))
          } catch {
            continue
          }

          if (payload.e === 'c' && payload.t) {
            accumulated += payload.t
            const parsed = parseRevBuffer(accumulated)
            if (parsed.length > 0) {
              setRevs(parsed)
              if (!transitionedRef.current && parsed[0].titulo.length > 3) {
                transitionedRef.current = true
                setScreen('revelaciones')
              }
            }
          } else if (payload.e === 'done') {
            setStreaming(false)
          } else if (payload.e === 'err') {
            throw new Error(payload.m ?? 'Error del servidor')
          }
        }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error desconocido'
      setError(msg)
      setScreen('form')
    } finally {
      setStreaming(false)
    }
  }

  const handleIndividualSubmit = async (data: FormData) => {
    setFormData(data)
    await runStream({ tipo: 'individual', ...data })
  }

  const handleParejaSubmit = async (data: ParejaData) => {
    setParejaData(data)
    await runStream({ tipo: 'pareja', ...data })
  }

  return (
    <>
      <div className="stars-bg" aria-hidden="true" />

      <main className="relative z-10 min-h-screen">

        {/* ── Selector ── */}
        {screen === 'selector' && (
          <div className="min-h-screen flex flex-col items-center justify-center px-4 py-16 relative z-10">
            <div className="text-center mb-12 animate-fade-in">
              <div className="text-3xl mb-4 tracking-widest text-gold-DEFAULT/50 select-none">
                ☽ · ✦ · ☾
              </div>
              <h1 className="font-cinzel text-4xl md:text-5xl gold-text tracking-wide mb-3">
                AstroGuía
              </h1>
              <p className="font-cinzel text-[10px] tracking-[0.45em] text-gold-DEFAULT/40 uppercase mb-6">
                Jyotish · Astrología Védica
              </p>
              <div className="gold-divider" />
            </div>

            <div className="grid md:grid-cols-2 gap-5 w-full max-w-2xl">
              <button
                onClick={() => { setTipo('individual'); setScreen('form') }}
                className="mystic-card mystic-card-hover rounded-2xl p-8 flex flex-col items-center text-center border border-gold-DEFAULT/25 shadow-[0_0_32px_rgba(212,175,55,0.06)] group transition-all duration-300"
              >
                <div className="text-5xl mb-5 select-none group-hover:scale-110 transition-transform duration-300">🌟</div>
                <h2 className="font-cinzel text-xl text-gold-DEFAULT tracking-wide mb-2">
                  Conoce tu carta
                </h2>
                <p className="text-white/45 font-garamond text-base leading-relaxed">
                  Descubre quién eres en esencia
                </p>
                <div className="mt-6 font-cinzel text-[9px] tracking-[0.35em] text-gold-DEFAULT/40 uppercase">
                  Carta védica individual ✦
                </div>
              </button>

              <button
                onClick={() => { setTipo('pareja'); setScreen('form') }}
                className="mystic-card mystic-card-hover rounded-2xl p-8 flex flex-col items-center text-center border border-rose-400/25 shadow-[0_0_32px_rgba(244,63,94,0.06)] group transition-all duration-300"
              >
                <div className="text-5xl mb-5 select-none group-hover:scale-110 transition-transform duration-300">💫</div>
                <h2 className="font-cinzel text-xl tracking-wide mb-2" style={{ color: '#fda4af' }}>
                  Conoce tu compatibilidad
                </h2>
                <p className="text-white/45 font-garamond text-base leading-relaxed">
                  Descubre cómo el cosmos ve tu relación
                </p>
                <div className="mt-6 font-cinzel text-[9px] tracking-[0.35em] uppercase" style={{ color: 'rgba(253,164,175,0.4)' }}>
                  Kundali Matching ✦
                </div>
              </button>
            </div>

            <p className="mt-12 text-white/20 text-sm font-garamond text-center">
              Dario Jiménez Medina — Jyotish · Bogotá, Colombia
            </p>
          </div>
        )}

        {/* ── Form — individual ── */}
        {screen === 'form' && tipo === 'individual' && (
          <LandingForm
            onSubmit={handleIndividualSubmit}
            error={error}
            onBack={() => { setError(null); setScreen('selector') }}
          />
        )}

        {/* ── Form — pareja ── */}
        {screen === 'form' && tipo === 'pareja' && (
          <ParejaForm
            onSubmit={handleParejaSubmit}
            error={error}
            onBack={() => { setError(null); setScreen('selector') }}
          />
        )}

        {/* ── Loading ── */}
        {screen === 'loading' && (
          <LoadingScreen nombre={loadingNombre} tipo={tipo} />
        )}

        {/* ── Revelaciones ── */}
        {screen === 'revelaciones' && (
          <Revelaciones
            nombre={revelacionNombre}
            revs={revs}
            streaming={streaming}
            tipo={tipo}
            onCTA={() => setScreen('upsell')}
            onBack={() => setScreen('selector')}
            apiUrl={API_URL}
            requestBody={
              tipo === 'pareja' && parejaData
                ? { tipo: 'pareja', ...parejaData }
                : { tipo: 'individual', ...(formData ?? { nombre: '', fecha: '', hora: '', ciudad: '' }) }
            }
          />
        )}

        {/* ── Upsell ── */}
        {screen === 'upsell' && (
          <Upsell
            nombre={revelacionNombre}
            tipo={tipo}
            onBack={() => setScreen('selector')}
          />
        )}

      </main>
    </>
  )
}
