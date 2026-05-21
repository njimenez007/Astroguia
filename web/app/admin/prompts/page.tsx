'use client'

import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { createClient } from '@/lib/supabase/client'
import AdminNav from '@/components/AdminNav'

type Tipo = 'carta' | 'predicciones' | 'compatibilidad'

const TABS: { tipo: Tipo; label: string; active: string }[] = [
  { tipo: 'carta',          label: 'Carta Astral',   active: 'text-gold-DEFAULT border-gold-DEFAULT/40 bg-gold-DEFAULT/6' },
  { tipo: 'predicciones',   label: 'Predicciones',   active: 'text-violet-400 border-violet-500/40 bg-violet-500/6' },
  { tipo: 'compatibilidad', label: 'Compatibilidad', active: 'text-rose-400 border-rose-400/40 bg-rose-400/6' },
]

export default function PromptsPage() {
  const [userEmail, setUserEmail]   = useState('')
  const [tipo, setTipo]             = useState<Tipo>('carta')
  const [prompts, setPrompts]       = useState<Record<Tipo, string>>({ carta: '', predicciones: '', compatibilidad: '' })
  const [loading, setLoading]       = useState(true)
  const [saving, setSaving]         = useState(false)
  const [savedOk, setSavedOk]       = useState(false)
  const [preview, setPreview]       = useState(false)
  const [updatedAt, setUpdatedAt]   = useState<Record<Tipo, string>>({ carta: '', predicciones: '', compatibilidad: '' })
  const fileInputRef                = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const supabase = createClient()
    void supabase.auth.getUser().then(res => {
      setUserEmail(res.data.user?.email ?? '')
    })
    void supabase.from('prompts').select('tipo, contenido, updated_at').then(({ data }) => {
      if (data) {
        const content: Record<Tipo, string>    = { carta: '', predicciones: '', compatibilidad: '' }
        const dates:   Record<Tipo, string>    = { carta: '', predicciones: '', compatibilidad: '' }
        for (const row of data) {
          if (row.tipo in content) {
            content[row.tipo as Tipo] = row.contenido
            dates[row.tipo as Tipo]   = row.updated_at
          }
        }
        setPrompts(content)
        setUpdatedAt(dates)
      }
      setLoading(false)
    })
  }, [])

  const handleSave = async () => {
    setSaving(true)
    setSavedOk(false)
    const supabase = createClient()
    const now = new Date().toISOString()
    const { error } = await supabase.from('prompts').upsert(
      { tipo, contenido: prompts[tipo], updated_at: now },
      { onConflict: 'tipo' }
    )
    setSaving(false)
    if (!error) {
      setSavedOk(true)
      setUpdatedAt(prev => ({ ...prev, [tipo]: now }))
      setTimeout(() => setSavedOk(false), 2500)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = ev => {
      const text = ev.target?.result as string
      setPrompts(prev => ({ ...prev, [tipo]: text }))
      setPreview(false)
    }
    reader.readAsText(file, 'utf-8')
    e.target.value = ''
  }

  const fmtDate = (iso: string) => {
    if (!iso) return ''
    return new Date(iso).toLocaleString('es-CO', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  }

  const activeTab = TABS.find(t => t.tipo === tipo)!

  return (
    <div className="relative min-h-screen">
      <div className="stars-bg" aria-hidden="true" />
      <AdminNav userEmail={userEmail} />

      <div className="relative z-10 max-w-4xl mx-auto px-4 py-8">

        {/* Header */}
        <div className="mb-6">
          <p className="font-cinzel text-[10px] tracking-[0.5em] text-gold-DEFAULT/40 uppercase mb-1">
            Editor de Prompts
          </p>
          <p className="font-garamond text-white/30 text-sm leading-relaxed">
            El system prompt que usará Claude al generar cada lectura.
            Usa <code className="text-gold-DEFAULT/60 bg-white/5 px-1 rounded text-xs">{'{nombre}'}</code> para insertar
            el nombre del cliente (en compatibilidad: <code className="text-gold-DEFAULT/60 bg-white/5 px-1 rounded text-xs">{'{nombre1}'}</code> y <code className="text-gold-DEFAULT/60 bg-white/5 px-1 rounded text-xs">{'{nombre2}'}</code>).
            Si el campo está vacío se usará el prompt por defecto del código.
          </p>
        </div>

        {/* Tabs + upload */}
        <div className="flex gap-2 mb-4 flex-wrap items-center">
          {TABS.map(tab => (
            <button
              key={tab.tipo}
              onClick={() => { setTipo(tab.tipo); setPreview(false) }}
              className={`font-cinzel text-[10px] tracking-[0.3em] uppercase px-4 py-2 rounded-full border transition-all ${
                tipo === tab.tipo
                  ? tab.active
                  : 'text-white/30 border-white/10 hover:border-white/20 hover:text-white/50'
              }`}
            >
              {tab.label}
            </button>
          ))}

          {/* File upload button */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".md,text/markdown,text/plain"
            onChange={handleFileUpload}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="ml-auto font-cinzel text-[9px] tracking-[0.3em] uppercase text-white/35 hover:text-gold-DEFAULT border border-white/10 hover:border-gold-DEFAULT/30 px-4 py-2 rounded-full transition-all flex items-center gap-2"
          >
            <span>↑</span> Subir .md
          </button>
        </div>

        {/* Last saved */}
        {updatedAt[tipo] && (
          <p className="font-garamond text-white/20 text-xs mb-2">
            Última actualización: {fmtDate(updatedAt[tipo])}
          </p>
        )}

        {/* Editor / Preview area */}
        <div className="mystic-card rounded-2xl border border-white/10 overflow-hidden">
          {loading ? (
            <div className="h-96 flex items-center justify-center">
              <span className="font-garamond text-white/30 animate-pulse">Cargando prompts...</span>
            </div>
          ) : preview ? (
            <div className="p-6 min-h-[60vh] overflow-y-auto prose prose-invert prose-sm max-w-none font-garamond text-white/75 leading-relaxed">
              {prompts[tipo]
                ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{prompts[tipo]}</ReactMarkdown>
                : <p className="text-white/25 italic">Sin contenido — se usará el prompt por defecto.</p>
              }
            </div>
          ) : (
            <textarea
              value={prompts[tipo]}
              onChange={e => setPrompts(prev => ({ ...prev, [tipo]: e.target.value }))}
              placeholder={`Escribe aquí el system prompt en Markdown para ${activeTab.label}...\n\nEjemplo:\nEres un Astrólogo Védico Maestro especializado en Jyotish...\n\nTu cliente se llama {nombre}.`}
              className="w-full h-[60vh] bg-transparent text-white/80 font-garamond text-sm p-6 outline-none resize-none placeholder-white/15 leading-relaxed"
              spellCheck={false}
            />
          )}
        </div>

        {/* Actions row */}
        <div className="flex items-center justify-between mt-4">
          <button
            onClick={() => setPreview(p => !p)}
            className="font-cinzel text-[9px] tracking-[0.3em] uppercase text-white/35 hover:text-white/60 border border-white/10 hover:border-white/20 px-4 py-2 rounded-full transition-colors"
          >
            {preview ? '← Editar' : 'Vista previa'}
          </button>

          <div className="flex items-center gap-3">
            {prompts[tipo] && (
              <button
                onClick={() => { setPrompts(prev => ({ ...prev, [tipo]: '' })) }}
                className="font-cinzel text-[9px] tracking-[0.3em] uppercase text-white/20 hover:text-red-400/60 border border-white/8 hover:border-red-400/20 px-3 py-2 rounded-full transition-colors"
              >
                Limpiar
              </button>
            )}
            <button
              onClick={handleSave}
              disabled={saving}
              className={`btn-gold px-6 py-2.5 rounded-full text-[10px] tracking-[0.3em] uppercase disabled:opacity-50 disabled:cursor-not-allowed transition-all ${
                savedOk ? 'opacity-80' : ''
              }`}
            >
              {saving ? 'Guardando...' : savedOk ? 'Guardado ✓' : 'Guardar Prompt'}
            </button>
          </div>
        </div>

        <p className="font-garamond text-white/15 text-xs mt-5 text-center">
          Los cambios se aplican inmediatamente en la próxima lectura generada
        </p>
      </div>
    </div>
  )
}
