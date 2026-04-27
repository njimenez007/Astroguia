"""AstroGuía — FastAPI backend."""
import sys
import asyncio
from pathlib import Path

# Add project root to sys.path so imports work regardless of CWD
ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

from src.api.engine import get_birth_data
from src.api.claude_hook import stream_hook
from src.api.claude_carta import generate_carta_astral

app = FastAPI(title="AstroGuía API", version="0.1.0")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}


@app.middleware("http")
async def add_cors(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=CORS_HEADERS)
    response = await call_next(request)
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response


class GanchoRequest(BaseModel):
    tipo: str = "individual"   # "individual" | "pareja"
    nombre: str
    fecha: str                 # YYYY-MM-DD
    hora: str                  # HH:MM
    ciudad: str
    # Solo para tipo="pareja"
    pareja_nombre: str | None = None
    pareja_fecha: str | None = None
    pareja_hora: str | None = None
    pareja_ciudad: str | None = None


@app.post("/api/gancho")
async def gancho(req: GanchoRequest) -> StreamingResponse:
    """
    Calcula la carta védica y hace streaming de revelaciones vía SSE.
    individual: 2 revelaciones (personalidad + predicción).
    pareja:     1 revelación de compatibilidad (requiere datos de los dos).
    """
    try:
        birth_data = await asyncio.to_thread(
            get_birth_data, req.nombre, req.fecha, req.hora, req.ciudad
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error calculando carta: {ex}")

    birth_data2 = None
    if req.tipo == "pareja" and req.pareja_nombre and req.pareja_fecha and req.pareja_hora and req.pareja_ciudad:
        try:
            birth_data2 = await asyncio.to_thread(
                get_birth_data, req.pareja_nombre, req.pareja_fecha, req.pareja_hora, req.pareja_ciudad
            )
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"Error calculando carta de pareja: {ex}")

    return StreamingResponse(
        stream_hook(birth_data, req.nombre, req.tipo, birth_data2, req.pareja_nombre),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


class CartaRequest(BaseModel):
    nombre: str
    fecha: str   # YYYY-MM-DD
    hora: str    # HH:MM
    ciudad: str


@app.post("/api/carta-completa")
async def carta_completa(req: CartaRequest) -> StreamingResponse:
    """
    Genera el informe completo de Carta Astral (5 bloques) vía SSE.
    Cada bloque emite: block_start → chunks → block_done.
    Al terminar todos: done.
    """
    try:
        birth_data = await asyncio.to_thread(
            get_birth_data, req.nombre, req.fecha, req.hora, req.ciudad
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error calculando carta: {ex}")

    return StreamingResponse(
        generate_carta_astral(birth_data, req.nombre),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "service": "AstroGuía API"}
