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
    nombre: str
    fecha: str   # YYYY-MM-DD
    hora: str    # HH:MM
    ciudad: str


@app.post("/api/gancho")
async def gancho(req: GanchoRequest) -> StreamingResponse:
    """
    Calcula la carta védica con get_birth_data() y hace streaming
    de las 4 revelaciones generadas por Claude vía Server-Sent Events.
    """
    try:
        # get_birth_data es sincrónico — lo corremos en un thread
        birth_data = await asyncio.to_thread(
            get_birth_data, req.nombre, req.fecha, req.hora, req.ciudad
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error calculando carta: {ex}")

    return StreamingResponse(
        stream_hook(birth_data, req.nombre),
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
