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
from src.api.claude_pregunta import stream_pregunta
from src.api.claude_predicciones import generate_predicciones
from src.api.claude_compatibilidad import generate_compatibilidad

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
    custom_system: str | None = None


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
        generate_carta_astral(birth_data, req.nombre, req.custom_system),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


class PreguntaRequest(BaseModel):
    tipo: str = "individual"
    pregunta: str
    nombre: str
    fecha: str
    hora: str
    ciudad: str
    pareja_nombre: str | None = None
    pareja_fecha: str | None = None
    pareja_hora: str | None = None
    pareja_ciudad: str | None = None


@app.post("/api/pregunta")
async def pregunta(req: PreguntaRequest) -> StreamingResponse:
    """Responde una pregunta específica del consultante usando el mini-prompt correcto."""
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
        stream_pregunta(
            req.pregunta, req.tipo, birth_data, req.nombre,
            birth_data2, req.pareja_nombre,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


class PrediccionesRequest(BaseModel):
    nombre: str
    fecha: str
    hora: str
    ciudad: str
    custom_system: str | None = None


@app.post("/api/predicciones")
async def predicciones(req: PrediccionesRequest) -> StreamingResponse:
    """Genera la Lectura de Predicciones (Sade Sati + Dashas) — 5 bloques vía SSE."""
    try:
        birth_data = await asyncio.to_thread(
            get_birth_data, req.nombre, req.fecha, req.hora, req.ciudad
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error calculando carta: {ex}")

    return StreamingResponse(
        generate_predicciones(birth_data, req.nombre, req.custom_system),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


class CompatibilidadRequest(BaseModel):
    nombre: str
    fecha: str
    hora: str
    ciudad: str
    pareja_nombre: str
    pareja_fecha: str
    pareja_hora: str
    pareja_ciudad: str
    custom_system: str | None = None


@app.post("/api/compatibilidad-completa")
async def compatibilidad_completa(req: CompatibilidadRequest) -> StreamingResponse:
    """Genera la Lectura de Compatibilidad (Kundali Matching) — 5 bloques vía SSE."""
    try:
        birth_data1 = await asyncio.to_thread(
            get_birth_data, req.nombre, req.fecha, req.hora, req.ciudad
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error calculando carta de persona 1: {ex}")

    try:
        birth_data2 = await asyncio.to_thread(
            get_birth_data, req.pareja_nombre, req.pareja_fecha, req.pareja_hora, req.pareja_ciudad
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error calculando carta de persona 2: {ex}")

    return StreamingResponse(
        generate_compatibilidad(birth_data1, req.nombre, birth_data2, req.pareja_nombre, req.custom_system),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


class BirthDataRequest(BaseModel):
    nombre: str
    fecha: str
    hora: str
    ciudad: str


@app.post("/api/birth-data")
async def birth_data(req: BirthDataRequest):
    """Retorna el JSON completo de datos natales (sin streaming) para renderizar gráficas."""
    try:
        data = await asyncio.to_thread(
            get_birth_data, req.nombre, req.fecha, req.hora, req.ciudad
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error calculando carta: {ex}")
    return data


@app.get("/health")
def health():
    return {"status": "ok", "service": "AstroGuía API"}
