'use client'

// Actualiza este número con el WhatsApp real de Dario (sin + ni espacios)
const WHATSAPP = '573XXXXXXXXX'

const PRODUCTS = [
  {
    emoji: '📜',
    name: 'Carta Astral',
    subtitle: 'Cita 1 · Manual de identidad',
    description:
      'Quién eres en esencia, tu Dharma, fortalezas y debilidades planetarias, y en qué momento cósmico exacto estás.',
    features: [
      '5 bloques de análisis profundo',
      '12 gráficas védicas',
      'Informe Word completo',
      'Audio ~1h con la voz de Dario',
    ],
    precio: '$90.000 – $120.000',
    moneda: 'COP',
    msg: '¡Hola Dario! Acabo de ver mis revelaciones gratis en AstroGuía y quiero mi *Carta Astral védica completa (Cita 1)* 🙏',
    featured: false,
  },
  {
    emoji: '🔮',
    name: 'Predicciones',
    subtitle: 'Cita 2 · Mapa temporal',
    description:
      'Qué períodos planetarios estás viviendo ahora, qué viene y cómo actuar estratégicamente en los próximos años.',
    features: [
      '4 bloques de predicción',
      '11 gráficas védicas',
      'Análisis Sade Sati completo',
      'Timing exacto de eventos clave',
    ],
    precio: '$90.000 – $120.000',
    moneda: 'COP',
    msg: '¡Hola Dario! Vi mis revelaciones en AstroGuía y quiero mi análisis de *Predicciones védicas (Cita 2)* 🔮',
    featured: true,
  },
  {
    emoji: '💫',
    name: 'Compatibilidad',
    subtitle: 'Kundali Matching · Dos personas',
    description:
      'Análisis védico de compatibilidad. Armonía emocional, karma compartido, potencial matrimonial y proyección 2026–2032.',
    features: [
      '12 secciones de análisis',
      '7 gráficas de ambas personas',
      'Ashta-Koota (36 puntos)',
      'Proyección temporal hasta 2032',
    ],
    precio: '$120.000 – $150.000',
    moneda: 'COP',
    msg: '¡Hola Dario! Quiero el análisis de *Compatibilidad de Pareja (Kundali Matching)* en AstroGuía 💫',
    featured: false,
  },
]

interface Props {
  nombre: string
}

export default function Upsell({ nombre }: Props) {
  const openWhatsApp = (msg: string) => {
    const url = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(msg)}`
    window.open(url, '_blank', 'noopener')
  }

  return (
    <div className="min-h-screen px-4 py-16 relative z-10">
      <div className="max-w-3xl mx-auto">

        {/* ── Header ── */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="text-3xl mb-3 tracking-widest text-gold-DEFAULT/50 select-none">
            ✦ &nbsp; ✦ &nbsp; ✦
          </div>
          <h1 className="font-cinzel text-3xl md:text-4xl gold-text tracking-wide mb-2">
            Tu Lectura Completa, {nombre}
          </h1>
          <p className="text-white/55 font-garamond text-xl max-w-xl mx-auto leading-relaxed">
            Elige el análisis que necesitas. Dario entrega un informe Word completo
            más un audio personal en su voz.
          </p>
          <div className="gold-divider mt-8" />
        </div>

        {/* ── Products ── */}
        <div className="grid md:grid-cols-3 gap-5">
          {PRODUCTS.map((product) => (
            <div
              key={product.name}
              className={`mystic-card mystic-card-hover rounded-2xl p-6 flex flex-col relative ${
                product.featured
                  ? 'border-gold-DEFAULT/50 shadow-[0_0_40px_rgba(212,175,55,0.1)]'
                  : ''
              }`}
            >
              {product.featured && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 whitespace-nowrap">
                  <span className="btn-gold text-[9px] tracking-[0.3em] px-4 py-1.5 rounded-full shadow-sm">
                    Más solicitado
                  </span>
                </div>
              )}

              <div className="text-4xl mb-4 select-none">{product.emoji}</div>

              <h2 className="font-cinzel text-gold-DEFAULT text-xl leading-snug mb-0.5">
                {product.name}
              </h2>
              <p className="font-cinzel text-[9px] tracking-[0.35em] text-gold-DEFAULT/40 uppercase mb-4">
                {product.subtitle}
              </p>

              <p className="text-white/65 font-garamond text-base leading-relaxed mb-5">
                {product.description}
              </p>

              <ul className="space-y-2 mb-6 flex-1">
                {product.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-white/55 font-garamond text-sm">
                    <span className="text-gold-DEFAULT/60 mt-0.5 text-xs flex-shrink-0">✦</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>

              <div>
                <p className="font-cinzel text-gold-DEFAULT text-2xl mb-1">
                  {product.precio}
                </p>
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

        {/* ── Trust signals ── */}
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
