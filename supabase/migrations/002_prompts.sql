-- Tabla para almacenar los system prompts personalizados por tipo de lectura
CREATE TABLE IF NOT EXISTS prompts (
  tipo       text PRIMARY KEY CHECK (tipo IN ('carta', 'predicciones', 'compatibilidad')),
  contenido  text NOT NULL DEFAULT '',
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE prompts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated can manage prompts"
  ON prompts FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE OR REPLACE FUNCTION update_prompts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prompts_updated_at
  BEFORE UPDATE ON prompts
  FOR EACH ROW EXECUTE FUNCTION update_prompts_updated_at();
