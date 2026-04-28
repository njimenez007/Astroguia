'use client'

import { useState } from 'react'

type Tipo = 'individual' | 'pareja'

interface Props {
  apiUrl: string
  requestBody: Record<string, string>
  tipo: Tipo
}

function Cursor() {
  return (
    <span
      className="inline-block w-[2px] h-[1.1em] bg-gold-DEFAULT/70 ml-0.5 align-middle animate-pulse"
      aria-hidden="true"
    />
  )
}

export default function MiniPregunta({ apiUrl, requestBody, tipo }: Props) {
  const [pregunta, setPregunta] = useState('')
  const [respuesta, setRespuesta] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [enviada, setEnviada] = useState(false)
  const [error, setError] = useState(false)

  const accentClass = tipo === 'pareja' ? 'text-rose-300/50' : 'text-gold-DEFAULT/40'
  const borderClass = tipo === 'pareja' ? 'border-rose-400/15' : 'border-gold-DEFAULT/15'
  const respBorderClass = tipo === 'pareja' ? 'border-rose-400/20' : 'border-gold-DEFAULT/20'
  const btnClass = tipo === 'pareja'
    ? 'w-full py-3 rounded-xl font-cinzel text-xs tracking-[0.2em] text-white disabled:opacity-30 disabled:cursor-not-allowed shadow-[0_2px_16px_rgba(244,63,94,0.15)]'
    : 'btn-gold w-full py-3 rounded-xl text-xs tracking-[0.2em] disabled:opacity-30 disabled:cursor-not-allowed'
  const btnStyle = tipo === 'pareja'
    ? { background: 'linear-gradient(135deg, #be185d, #f43f5e, #fb7185)' }
    : undefined

  const placeholder = tipo === 'pareja'
    ? '¿Hay algo específico que quieran saber sobre su relación?'
    : '¿Hay algo específico que quieras preguntarle al cosmos?'

  const handleSubmit = async () => {
    if (!pregunta.trim() || streaming) return
    setEnviada(true)
    setStreaming(true)
    setRespuesta('')
    setError(false)

    try {
      const resp = await fetch(`${apiUrl}/api/pregunta`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...requestBody, pregunta }),
      })

      if (!resp.ok) throw new Error(`Error ${resp.status}`)

      const reader = resp.body!.getReader()
      const decoder = new TextDecoder()
      let remainder = ''

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
          try { payload = JSON.parse(line.slice(6)) } catch { continue }

          if (payload.e === 'c' && payload.t) {
            setRespuesta(prev => prev + payload.t)
          } else if (payload.e === 'done') {
            setStreaming(false)
          } else if (payload.e === 'err') {
            throw new Error(payload.m)
          }
        }
      }
    } catch {
      setStreaming(false)
      setError(true)
    }
  }

  const handleNueva = () => {
    setPregunta('')
    setRespuesta('')
    setEnviada(false)
    setError(false)
  }

  return (
    <div className="mt-14">
      <div className="gold-divider mb-8" />

      <div className="text-center mb-6">
        <p className={`font-cinzel text-[10px] tracking-[0.4em] uppercase mb-3 ${accentClass}`}>
          ✦ &nbsp; Pregunta al cosmos
        </p>
        <p className="text-white/55 font-garamond text-lg">
          ¿Tienes una pregunta específica para los astros?
        </p>
      </div>

      {!enviada ? (
        <div className={`mystic-card rounded-2xl p-6 border ${borderClass}`}>
          <textarea
            value={pregunta}
            onChange={e => setPregunta(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit() } }}
            placeholder={placeholder}
            rows={3}
            className="w-full bg-transparent text-white/80 font-garamond text-base resize-none focus:outline-none placeholder:text-white/25 border-b border-white/10 pb-3 mb-4"
          />
          <button
            onClick={handleSubmit}
            disabled={!pregunta.trim() || streaming}
            className={btnClass}
            style={btnStyle}
          >
            Pregúntale al cosmos &nbsp;✦
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className={`mystic-card rounded-2xl p-5 border ${borderClass}`}>
            <p className={`font-cinzel text-[9px] tracking-[0.35em] uppercase mb-2 ${accentClass}`}>
              Tu pregunta
            </p>
            <p className="text-white/50 font-garamond text-base italic">{pregunta}</p>
          </div>

          <div className={`mystic-card rounded-2xl p-6 border ${respBorderClass}`}>
            <p className={`font-cinzel text-[9px] tracking-[0.35em] uppercase mb-4 ${accentClass}`}>
              ✦ &nbsp; El cosmos responde
            </p>
            {error ? (
              <p className="text-red-400/70 font-garamond text-sm">
                Algo salió mal. Intenta de nuevo.
              </p>
            ) : (
              <p className="text-white/82 font-garamond text-[1.05rem] leading-[1.8] whitespace-pre-wrap">
                {respuesta}
                {streaming && <Cursor />}
              </p>
            )}
          </div>

          {!streaming && (
            <button
              onClick={handleNueva}
              className={`font-cinzel text-[10px] tracking-[0.3em] uppercase transition-colors block mx-auto px-4 py-2 rounded-full border border-white/15 hover:border-gold-DEFAULT/40 ${accentClass} hover:text-gold-DEFAULT`}
            >
              Hacer otra pregunta
            </button>
          )}
        </div>
      )}
    </div>
  )
}
