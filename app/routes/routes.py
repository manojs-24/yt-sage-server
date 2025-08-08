from fastapi import APIRouter
from app.schemas import  SuccessResponse, ErrorResponse, YouTubeAnalysisRequest
from app.controllers.controller import handle_youtube_analysis
from datetime import datetime

router = APIRouter()

# ✅ Root route
@router.get("/", response_model=SuccessResponse)
def root():
    return SuccessResponse(
        message= "Welcome to Yt-Sage - Focused on YouTube wisdom",
        data={"data": "Hii !"},
        timestamp=datetime.utcnow()
    ).to_response()


# ✅ Health check route
@router.get("/health", response_model=SuccessResponse)
def health_check():
    return SuccessResponse(
        message= "Server is healthy.",
        data={"status": "ok"},
        timestamp=datetime.utcnow()
    ).to_response()



@router.post("/yt-sage", response_model=SuccessResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
def analyse_video(payload: YouTubeAnalysisRequest):
    return handle_youtube_analysis(payload)

