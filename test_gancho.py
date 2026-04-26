"""Test end-to-end del gancho — imprime las 4 revelaciones de Nicolas."""
import asyncio
import json
import sys
import os

# Force UTF-8 output on Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

sys.path.insert(0, os.path.dirname(__file__))

from src.api.engine import get_birth_data
from src.api.claude_hook import stream_hook


async def main() -> None:
    print("=" * 65)
    print("  AstroGuia -- Test End-to-End | Gancho Gratuito")
    print("=" * 65)
    print()

    nombre = "Nicolas Jimenez"
    fecha  = "2003-03-28"
    hora   = "08:07"
    ciudad = "Bogotá, Colombia"

    print(f"Calculando carta de {nombre}")
    print(f"  {fecha} {hora} - {ciudad}")
    print()

    birth_data = get_birth_data(nombre, fecha, hora, ciudad)

    # Resumen rápido
    lagna     = birth_data["d1"]["lagna"]["signo"]
    nk_data   = birth_data.get("nakshatra_luna", {})
    nakshatra = nk_data.get("nombre", "?")
    ss        = birth_data.get("sade_sati", {})
    activo    = ss.get("activo_hoy", False)
    fase      = ss.get("fase_actual", "—")

    from prompts.gancho import _current_dasha
    dasha = _current_dasha(birth_data, __import__("datetime").date.today().isoformat())
    dasha_str = f"{dasha.get('planeta','?')} ({dasha.get('inicio','')[:4]}–{dasha.get('fin','')[:4]})"

    print(f"   Lagna:           {lagna}")
    print(f"   Nakshatra Luna:  {nakshatra}")
    print(f"   Mahadasha:       {dasha_str}")
    print(f"   Sade Sati hoy:   {'Activo — ' + str(fase) if activo else 'No activo'}")
    print()
    print("Generando revelaciones con Claude (streaming)...")
    print("-" * 65)
    print()

    async for sse_line in stream_hook(birth_data, nombre):
        if not sse_line.startswith("data: "):
            continue
        try:
            payload = json.loads(sse_line[6:])
        except json.JSONDecodeError:
            continue

        if payload["e"] == "c":
            print(payload["t"], end="", flush=True)
        elif payload["e"] == "done":
            print()
            print()
            print("-" * 65)
            print("OK  Stream completado.")
            break
        elif payload["e"] == "err":
            print(f"\n❌  Error: {payload['m']}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
