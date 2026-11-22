from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.air_quality import router as air_quality_router
from app.api.guidance import router as guidance_router
from app.core.config import settings

app=FastAPI(title="BreatheWise AI API",description="Location-aware air-quality intelligence and household guidance.",version="0.3.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["Content-Type","Authorization"])
app.include_router(air_quality_router)
app.include_router(guidance_router)

@app.get("/",tags=["meta"])
async def root()->dict[str,str]:
    return {"name":"BreatheWise AI API","version":"0.3.0","docs":"/docs","health":"/health"}

@app.get("/health",tags=["meta"])
async def health()->dict[str,str]:
    return {"status":"ok","service":"breathewise-api"}
