from fastapi import FastAPI

from api.routes import diffusion, health, multimodal, reviews

app = FastAPI(title="Enterprise Diffusion and Multimodal AI", version="0.1.0")
app.include_router(health.router)
app.include_router(diffusion.router)
app.include_router(multimodal.router)
app.include_router(reviews.router)
