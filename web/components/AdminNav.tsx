'use client'

import { useRouter, usePathname } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'

interface Props {
  userEmail: string
  title?: string
}

const NAMES: Record<string, string> = {
  'dariojimed07@gmail.com': 'Dario',
  'nicojime14@gmail.com':   'Nicolás',
}

const NAV = [
  { href: '/admin/dashboard', label: 'Lecturas' },
  { href: '/admin/validar',   label: 'Cartas'   },
  { href: '/admin/prompts',   label: 'Prompts'  },
  { href: '/admin/nueva',     label: 'Nueva'    },
]

export default function AdminNav({ userEmail }: Props) {
  const router   = useRouter()
  const pathname = usePathname()

  const handleLogout = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/admin')
    router.refresh()
  }

  const displayName = NAMES[userEmail] ?? userEmail.split('@')[0]

  return (
    <div className="sticky top-0 z-50 bg-mystic-900/95 backdrop-blur-md border-b border-white/[0.06] print:hidden">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-4">

        {/* Logo */}
        <button
          onClick={() => router.push('/admin/dashboard')}
          className="font-cinzel text-[10px] tracking-[0.4em] text-gold-DEFAULT/55 hover:text-gold-DEFAULT transition-colors uppercase shrink-0"
        >
          AstroGuía
        </button>

        {/* Nav links */}
        <div className="flex items-center gap-1 flex-1">
          {NAV.map(link => {
            const active =
              pathname === link.href ||
              (link.href !== '/admin/dashboard' && pathname?.startsWith(link.href))
            return (
              <button
                key={link.href}
                onClick={() => router.push(link.href)}
                className={`font-cinzel text-[9px] tracking-[0.3em] uppercase px-3 py-1.5 rounded-full transition-all ${
                  active
                    ? 'text-gold-DEFAULT bg-gold-DEFAULT/8 border border-gold-DEFAULT/20'
                    : 'text-white/28 hover:text-white/55 border border-transparent'
                }`}
              >
                {link.label}
              </button>
            )
          })}
        </div>

        {/* User + logout */}
        <div className="flex items-center gap-3 shrink-0">
          <span className="font-garamond text-white/35 text-sm hidden sm:block">
            {displayName}
          </span>
          <button
            onClick={handleLogout}
            className="font-cinzel text-[9px] tracking-[0.3em] text-white/35 hover:text-white/60 transition-colors border border-white/10 hover:border-white/20 px-3 py-1.5 rounded-full uppercase"
          >
            Salir
          </button>
        </div>
      </div>
    </div>
  )
}
