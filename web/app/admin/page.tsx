'use client'

import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'
import { Suspense } from 'react'

function LoginContent() {
  const params = useSearchParams()
  const error = params.get('error')

  const handleGoogleLogin = async () => {
    const supabase = createClient()
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    })
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4">
      <div className="stars-bg" aria-hidden="true" />

      <div className="relative z-10 w-full max-w-sm">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="text-2xl mb-4 tracking-widest text-gold-DEFAULT/45 select-none">
            ☽ · ✦ · ☾
          </div>
          <h1 className="font-cinzel text-3xl gold-text tracking-wide mb-2">
            AstroGuía
          </h1>
          <p className="font-cinzel text-[10px] tracking-[0.5em] text-gold-DEFAULT/38 uppercase mb-1">
            Panel de Administración
          </p>
          <p className="font-garamond text-white/35 text-base">
            Dario Jiménez Medina · Jyotish
          </p>
          <div className="gold-divider mt-6" />
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 px-4 py-3 rounded-xl border border-red-500/25 bg-red-500/8 text-center">
            <p className="font-garamond text-red-400/80 text-sm">
              {error === 'unauthorized'
                ? 'Este email no tiene acceso al panel.'
                : 'Error al iniciar sesión. Intenta de nuevo.'}
            </p>
          </div>
        )}

        {/* Login card */}
        <div className="mystic-card rounded-2xl p-8 border border-gold-DEFAULT/15 text-center">
          <p className="font-garamond text-white/50 text-base mb-6">
            Acceso exclusivo para el equipo de AstroGuía.
          </p>
          <button
            onClick={handleGoogleLogin}
            className="btn-gold w-full py-4 rounded-xl text-xs tracking-[0.2em] shadow-[0_4px_24px_rgba(212,175,55,0.15)] flex items-center justify-center gap-3"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Continuar con Google
          </button>
        </div>

        <p className="text-center text-white/18 font-garamond text-sm mt-8">
          Solo Dario y Nicolás tienen acceso.
        </p>
      </div>
    </div>
  )
}

export default function AdminLoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen" />}>
      <LoginContent />
    </Suspense>
  )
}
