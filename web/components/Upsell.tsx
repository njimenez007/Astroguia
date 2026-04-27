'use client'

const WHATSAPP = '573XXXXXXXXX'

type Tipo = 'individual' | 'pareja'

const PRODUCTS_INDIVIDUAL = [
  {
    emoji: '📜',
    name: 'Carta Astral',
    subtitle: 'Cita 1 · Manual de identidad',
    description: 'Quién eres en esencia, tu Dharma, fortalezas y debilidades planetarias, y en qué momento cósmico exacto estás.',
    features: ['5 bloques de análisis profundo', '12 gráficas védicas', 'Informe Word completo', 'Audio ~1h con la voz de Dario'],
    precio: '$90.000 – $120.000',
    moneda: 'COP',
    msg: '¡Hola Dario! Acabo de ver mis revelaciones gratis en AstroGuía y quiero mi *Carta Astral védica completa (Cita 1)* 🙏',
    featured: true,
  },
  {
    emoji: '🔮',
    name: 'Predicciones',
    subtitle: 'Cita 2 · Mapa temporal',
    description: 'Qué períodos planetarios estás viviendo ahora, qué viene y cómo actuar estratégicamente en los próximos años.',
    features: ['4 bloques de predicción', '11 gráficas védicas', 'Análisis Sade Sati completo', 'Timing exacto de eventos clave'],
    precio: '$90.000 – $120.000',
    moneda: 'COP',
    msg: '¡Hola Dario! Vi mis revelaciones en AstroGuía y quiero mi análisis de *Predicciones védicas (Cita 2)* 🔮',
    featured: false,
  },
]

const PRODUCT_PAREJA = {
  emoji: '💫',
  name: 'Compatibilidad de Pareja',
  subtitle: 'Kundali Matching · Análisis completo',
  description: 'El análisis védico más profundo de su relación. Armonía emocional, karma compartido, potencial matrimonial y proyección temporal.',
  features: ['12 secciones de análisis', '7 gráficas de ambas personas', 'Ashta-Koota (36 puntos)', 'Proyección temporal hasta 2032', 'Audio personal de Dario'],
  precio: '$120.000 – $150.000',
  moneda: 'COP',
  msg: '¡Hola Dario! Vi nuestra revelación de compatibilidad en AstroGuía y quiero el análisis completo de *Compatibilidad de Pareja (Kundali Matching)* 💫',
}

interface Props {
  nombre: string
  tipo?: Tipo
}

export default function Upsell({ nombre, tipo = 'individual' }: Props) {
  const openWhatsApp = (msg: string) => {
    const url = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(msg)}`
    window.open(url, '_blank', 'noopener')
  }

  if (tipo === 'pareja') {
    const p = PRODUCT_PAREJA
    return (
      <div className="min-h-screen px-4 py-16 relative z-10">
        <div className="max-w-lg mx-auto">

          <div className="text-center mb-10 animate-fade-in">
            <div className="text-3xl mb-3 tracking-widest select-none" style={{ color: 'rgba(244,63,94,0.5)' }}>
              ♡ &nbsp; ✦ &nbsp; ♡
            </div>
            <h1 className="font-cinzel text-3xl md:text-4xl tracking-wide mb-2" style={{ color: '#fda4af' }}>
              Su Análisis Completo
            </h1>
            <p className="text-white/45 font-garamond text-xl max-w-sm mx-auto leading-relaxed">
              El cosmos tiene mucho más que decir sobre {nombre} y su pareja.
            </p>
            <div className="h-px bg-gradient-to-r from-transparent via-rose-400/30 to-transparent mt-6" />
          </div>

          <div className="mystic-card rounded-2xl p-8 border border-rose-400/25 shadow-[0_0_40px_rgba(244,63,94,0.08)]">
            <div className="text-5xl mb-4 select-none text-center">{p.emoji}</div>
            <h2 className="font-cinzel text-2xl text-center mb-1" style={{ color: '#fda4af' }}>{p.name}</h2>
            <p className="font-cinzel text-[9px] tracking-[0.35em] text-center mb-5" style={{ color: 'rgba(253,164,175,0.4)' }}>{p.subtitle.toUpperCase()}</p>
            <p className="text-white/65 font-garamond text-lg leading-relaxed mb-6 text-center">{p.description}</p>
            <ul className="space-y-2 mb-8">
              {p.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-white/55 font-garamond">
                  <span className="text-rose-400/60 mt-0.5 text-xs flex-shrink-0">✦</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <div className="text-center mb-6">
              <p className="font-cinzel text-3xl mb-1" style={{ color: '#fda4af' }}>{p.precio}</p>
              <p className="text-white/30 text-xs font-garamond">{p.moneda}</p>
            </div>
            <button
              onClick={() => openWhatsApp(p.msg)}
              className="w-full py-4 rounded-xl font-cinzel text-sm tracking-[0.18em] text-white shadow-[0_2px_20px_rgba(244,63,94,0.2)]"
              style={{ background: 'linear-gradient(135deg, #be185d, #f43f5e, #fb7185, #f43f5e)', backgroundSize: '200% auto' }}
            >
              Quiero este análisis &nbsp;✦
            </button>
          </div>

          <div className="mt-10 text-center">
            <div className="gold-divider mb-6" />
            <div className="flex flex-wrap items-center justify-center gap-6 text-white/30 text-sm font-garamond">
              <span>🙏 +30 lecturas entregadas</span>
              <span className="text-white/15">·</span>
              <span>🎙️ Audio personal de Dario</span>
            </div>
            <p className="mt-4 text-white/20 text-xs font-garamond">Dario Jiménez Medina — Jyotish · Bogotá, Colombia</p>
          </div>
        </div>
      </div>
    )
  }

  // Flujo individual
  return (
    <div className="min-h-screen px-4 py-16 relative z-10">
      <div className="max-w-3xl mx-auto">

        <div className="text-center mb-12 animate-fade-in">
          <div className="text-3xl mb-3 tracking-widest text-gold-DEFAULT/50 select-none">✦ &nbsp; ✦ &nbsp; ✦</div>
          <h1 className="font-cinzel text-3xl md:text-4xl gold-text tracking-wide mb-2">
            Tu Lectura Completa, {nombre}
          </h1>
          <p className="text-white/55 font-garamond text-xl max-w-xl mx-auto leading-relaxed">
            Elige el análisis que necesitas. Dario entrega un informe completo más un audio personal en su voz.
          </p>
          <div className="gold-divider mt-8" />
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {PRODUCTS_INDIVIDUAL.map((product) => (
            <div
              key={product.name}
              className={`mystic-card mystic-card-hover rounded-2xl p-6 flex flex-col relative ${
                product.featured ? 'border-gold-DEFAULT/50 shadow-[0_0_40px_rgba(212,175,55,0.1)]' : ''
              }`}
            >
              {product.featured && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 whitespace-nowrap">
                  <span className="btn-gold text-[9px] tracking-[0.3em] px-4 py-1.5 rounded-full shadow-sm">
                    Recomendado
                  </span>
                </div>
              )}
              <div className="text-4xl mb-4 select-none">{product.emoji}</div>
              <h2 className="font-cinzel text-gold-DEFAULT text-xl leading-snug mb-0.5">{product.name}</h2>
              <p className="font-cinzel text-[9px] tracking-[0.35em] text-gold-DEFAULT/40 uppercase mb-4">{product.subtitle}</p>
              <p className="text-white/65 font-garamond text-base leading-relaxed mb-5">{product.description}</p>
              <ul className="space-y-2 mb-6 flex-1">
                {product.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-white/55 font-garamond text-sm">
                    <span className="text-gold-DEFAULT/60 mt-0.5 text-xs flex-shrink-0">✦</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <div>
                <p className="font-cinzel text-gold-DEFAULT text-2xl mb-1">{product.precio}</p>
                <p className="text-white/30 text-xs font-garamond mb-4">{product.moneda}</p>
                <button
                  onClick={() => openWhatsApp(product.msg)}
                  className="btn-gold w-full py-3 rounded-xl text-xs tracking-[0.2em] shadow-[0_2px_16px_rgba(212,175,55,0.15)]"
                >
                  Quiero este &nbsp;✦
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <div className="gold-divider mb-8" />
          <div className="flex flex-wrap items-center justify-center gap-6 text-white/30 text-sm font-garamond">
            <span>🙏 +30 lecturas entregadas</span>
            <span className="text-white/15">·</span>
            <span>🎙️ Audio personal de Dario</span>
            <span className="text-white/15">·</span>
            <span>📄 Informe Word completo</span>
          </div>
          <p className="mt-4 text-white/20 text-xs font-garamond">
            Dario Jiménez Medina — Jyotish · Bogotá, Colombia
          </p>
        </div>
      </div>
    </div>
  )
}
