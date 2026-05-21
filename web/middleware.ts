import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

// Únicos emails con acceso al panel de administración
const ALLOWED_EMAILS = ['dariojimed07@gmail.com', 'nicojime14@gmail.com']

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet: Array<{ name: string; value: string; options?: CookieOptions }>) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  // Refresh session
  const { data: { user } } = await supabase.auth.getUser()

  const path = request.nextUrl.pathname
  const isAdminRoot = path === '/admin'
  const isAdminProtected = path.startsWith('/admin/') || path === '/admin/dashboard'

  // Si está en ruta protegida y no hay sesión → login
  if (isAdminProtected && !user) {
    return NextResponse.redirect(new URL('/admin', request.url))
  }

  // Si hay sesión pero el email no está permitido → bloquear
  if (user && !ALLOWED_EMAILS.includes(user.email ?? '')) {
    await supabase.auth.signOut()
    return NextResponse.redirect(new URL('/admin?error=unauthorized', request.url))
  }

  // Si ya está autenticado y va al login → redirigir al dashboard
  if (isAdminRoot && user && ALLOWED_EMAILS.includes(user.email ?? '')) {
    return NextResponse.redirect(new URL('/admin/dashboard', request.url))
  }

  return supabaseResponse
}

export const config = {
  matcher: ['/admin/:path*', '/auth/:path*'],
}
