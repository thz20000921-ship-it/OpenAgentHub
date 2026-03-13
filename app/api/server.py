import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.database import init_db
from app.api.endpoints import api_router
from app.services.registry_service import RegistryService

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("✅ System initialized. Waiting for health check triggers.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A self-hosted AI agent registry and health-check platform.",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# 配置简易 Dashboard 模板
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", include_in_schema=False)
async def dashboard(request: Request, q: str = "", status: str = ""):
    """渲染简易自托管 Dashboard, 展示内置监控和查询面板"""
    tools = RegistryService.search_tools(q=q, status=status)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "tools": tools, "q": q, "status": status, "api_key": settings.API_KEY}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.server:app", host="127.0.0.1", port=8000, reload=True)
