import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AstroGuía — Jyotish · Astrología Védica en Español',
  description:
    'Descubre tu carta védica personalizada. Jyotish con la metodología de Dario Jiménez Medina — Astrólogo Védico.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="antialiased">{children}</body>
    </html>
  )
}
