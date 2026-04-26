'use client'

import { useRef, useState } from 'react'
import LandingForm, { FormData } from '@/components/LandingForm'
import LoadingScreen from '@/components/LoadingScreen'
import Revelaciones from '@/components/Revelaciones'
import Upsell from '@/components/Upsell'

type Screen = 'landing' | 'loading' | 'revelaciones' | 'upsell'

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
  const [screen, setScreen] = useState<Screen>('landing')
  const [formData, setFormData] = useState<FormData | null>(null)
  const [revs, setRevs] = useState<RevStream[]>([])
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const transitionedRef = useRef(false)

  const handleSubmit = async (data: FormData) => {
    setFormData(data)
    setError(null)
    setRevs([])
    setStreaming(true)
    transitionedRef.current = false
    setScreen('loading')

    try {
      const resp = await fetch(`${API_URL}/api/gancho`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
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
      setScreen('landing')
    } finally {
      setStreaming(false)
    }
  }

  return (
    <>
      <div className="stars-bg" aria-hidden="true" />

      <main className="relative z-10 min-h-screen">
        {screen === 'landing' && (
          <LandingForm onSubmit={handleSubmit} error={error} />
        )}

        {screen === 'loading' && (
          <LoadingScreen nombre={formData?.nombre ?? ''} />
        )}

        {screen === 'revelaciones' && (
          <Revelaciones
            nombre={formData?.nombre ?? ''}
            revs={revs}
            streaming={streaming}
            onCTA={() => setScreen('upsell')}
          />
        )}

        {screen === 'upsell' && (
          <Upsell nombre={formData?.nombre ?? ''} />
        )}
      </main>
    </>
  )
}
