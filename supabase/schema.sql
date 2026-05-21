-- AstroGuía — Supabase Schema
-- Ejecutar en: Supabase Dashboard → SQL Editor → New query

-- ─── CLIENTES ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.clientes (
  id                UUID    DEFAULT gen_random_uuid() PRIMARY KEY,
  nombre            TEXT    NOT NULL,
  fecha_nacimiento  DATE    NOT NULL,
  hora_nacimiento   TIME    NOT NULL,
  ciudad            TEXT    NOT NULL,
  email             TEXT,
  telefono          TEXT,
  notas             TEXT,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  created_by        UUID    REFERENCES auth.users(id)
);

ALTER TABLE public.clientes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Solo usuarios autenticados" ON public.clientes
  FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- ─── LECTURAS ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.lecturas (
  id               UUID    DEFAULT gen_random_uuid() PRIMARY KEY,
  cliente_id       UUID    REFERENCES public.clientes(id) ON DELETE CASCADE,
  tipo             TEXT    NOT NULL CHECK (tipo IN ('carta', 'predicciones', 'compatibilidad')),
  estado           TEXT    NOT NULL DEFAULT 'pendiente'
                           CHECK (estado IN ('pendiente', 'generando', 'completo', 'error')),
  contenido        JSONB   DEFAULT '[]'::jsonb,
  -- Solo para compatibilidad:
  pareja_nombre    TEXT,
  pareja_fecha     DATE,
  pareja_hora      TIME,
  pareja_ciudad    TEXT,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  created_by       UUID    REFERENCES auth.users(id)
);

ALTER TABLE public.lecturas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Solo usuarios autenticados" ON public.lecturas
  FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- ─── ÍNDICES ─────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_lecturas_cliente_id  ON public.lecturas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_lecturas_created_at  ON public.lecturas(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lecturas_tipo        ON public.lecturas(tipo);
