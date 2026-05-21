# Panel Admin — Instrucciones de Setup

## 1. Crear el proyecto Supabase (5 minutos)

1. Ir a **[supabase.com](https://supabase.com)** → "Start your project"
2. Crear cuenta con GitHub o Google
3. "New project" → Organization: Personal → Name: `astroguia` → Region: US East (N. Virginia)
4. Anotar la contraseña que piden → "Create new project"
5. Esperar ~2 minutos a que el proyecto se inicie

## 2. Copiar las credenciales

En Supabase Dashboard → **Settings → API**:
- Copiar **Project URL** (formato: `https://xxxxxxxxxxxx.supabase.co`)
- Copiar **anon public** key (la key larga que dice "safe to use in a browser")

Pegar ambos valores en `web/.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
```

## 3. Crear las tablas

En Supabase Dashboard → **SQL Editor** → "New query" → pegar el contenido de `supabase/schema.sql` → "Run"

Debe aparecer "Success. No rows returned."

## 4. Activar Google OAuth

En Supabase Dashboard → **Authentication → Providers → Google**:

1. Toggle "Enable" → ON
2. Necesitas una **Google OAuth App**:
   - Ir a [console.cloud.google.com](https://console.cloud.google.com)
   - Crear proyecto → "APIs & Services" → "OAuth consent screen"
     - User type: External → Create
     - App name: AstroGuía → Support email: tu email → Save
   - "Credentials" → "+ Create Credentials" → "OAuth client ID"
     - Application type: **Web application**
     - Name: AstroGuía Admin
     - Authorized redirect URIs: agregar la URL que muestra Supabase (formato: `https://xxxx.supabase.co/auth/v1/callback`)
     - → Create
   - Copiar **Client ID** y **Client Secret**
3. Pegar el Client ID y Client Secret en el panel de Supabase → Save

## 5. Configurar dominio en Supabase (para Vercel)

En Supabase Dashboard → **Authentication → URL Configuration**:
- Site URL: `https://tu-dominio.vercel.app`
- Redirect URLs: agregar `https://tu-dominio.vercel.app/auth/callback`

Para desarrollo local, agregar también: `http://localhost:3000/auth/callback`

## 6. Variables de entorno en Vercel

En Vercel Dashboard → Settings → Environment Variables, agregar:
- `NEXT_PUBLIC_SUPABASE_URL` = (mismo valor que en .env.local)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` = (mismo valor que en .env.local)

## Resultado final

Con todo configurado:
- Ir a `/admin` → aparece botón "Continuar con Google"
- Dario (`dariojimed07@gmail.com`) y Nicolás (`nicojime14@gmail.com`) pueden entrar
- Cualquier otro email es bloqueado
- Las lecturas generadas se guardan automáticamente en Supabase
- El historial muestra todas las lecturas anteriores
