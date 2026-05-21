'use client'

import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'

interface Props {
  userEmail: string
  title?: string
}

const NAMES: Record<string, string> = {
  'dariojimed07@gmail.com': 'Dario',
  'nicojime14@gmail.com': 'Nicolás',
}

export default function AdminNav({ userEmail, title }: Props) {
  const router = useRouter()

  const handleLogout = async () => {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/admin')
    router.refresh()
  }

  const displayName = NAMES[userEmail] ?? userEmail.split('@')[0]

  return (
    <div className="sticky top-0 z-50 bg-mystic-900/95 backdrop-blur-md border-b border-white/[0.06]">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-4">
        {/* Logo */}
        <button
          onClick={() => router.push('/admin/dashboard')}
          className="font-cinzel text-[10px] tracking-[0.4em] text-gold-DEFAULT/55 hover:text-gold-DEFAULT transition-colors uppercase"
        >
          AstroGuía · Admin
        </button>

        {/* Title */}
        {title && (
          <span className="font-cinzel text-[9px] tracking-[0.35em] text-white/22 uppercase flex-1 text-center truncate">
            {title}
          </span>
        )}
        {!title && <span className="flex-1" />}

        {/* User + logout */}
        <div className="flex items-center gap-3">
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
