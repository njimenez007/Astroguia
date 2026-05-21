import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse, type NextRequest } from 'next/server'

const ALLOWED_EMAILS = ['dariojimed07@gmail.com', 'nicojime14@gmail.com']

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')

  if (code) {
    const cookieStore = await cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() { return cookieStore.getAll() },
          setAll(cookiesToSet: Array<{ name: string; value: string; options?: CookieOptions }>) {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          },
        },
      }
    )

    const { data, error } = await supabase.auth.exchangeCodeForSession(code)

    if (!error && data.user) {
      if (ALLOWED_EMAILS.includes(data.user.email ?? '')) {
        return NextResponse.redirect(`${origin}/admin/dashboard`)
      }
      // Email no autorizado
      await supabase.auth.signOut()
      return NextResponse.redirect(`${origin}/admin?error=unauthorized`)
    }
  }

  return NextResponse.redirect(`${origin}/admin?error=auth_failed`)
}
