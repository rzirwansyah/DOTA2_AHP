from fastapi import FastAPI, APIRouter
from app.api.endpoints import authentication, heroes, criterias, matches, recommendations, history

app = FastAPI(
    title="Dota 2 Hero Recommendation API",
    description="REST API untuk memberikan rekomendasi hero Dota 2 menggunakan metode AHP.",
    version="1.0.0"
)

# Membuat prefix untuk semua endpoint
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(authentication.router, prefix="/authentication", tags=["Authentication"])
api_router.include_router(heroes.router, prefix="/heroes", tags=["Heroes"])
api_router.include_router(criterias.router, prefix="/criterias", tags=["Criterias"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(history.router, tags=["History"]) # Gabungkan history dan result

app.include_router(api_router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Dota 2 AHP Recommendation API"}