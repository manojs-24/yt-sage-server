from app.schemas import SuccessResponse, ErrorResponse, YouTubeAnalysisRequest
from app.utils.validations import is_valid_youtube_url
from app.services.youtube_service import extract_video_id, fetch_transcript, fetch_transcript_supadata, ask_question_to_gemini, ask_question_from_youtube
from youtube_transcript_api._errors import (
    TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, CouldNotRetrieveTranscript
)
from datetime import datetime

MAX_TRANSCRIPT_WORDS = 35000 


def handle_youtube_analysis(payload: YouTubeAnalysisRequest):
    url_string = str(payload.url)
    if not is_valid_youtube_url(url_string):
        return ErrorResponse(
            message="Invalid YouTube URL.",
            error="URL validation failed",
            timestamp=datetime.utcnow()
        ).to_response(status_code=400)
    else:
        print("Valid Youtube URL")

    try:
        video_id = extract_video_id(url_string)
        transcript = fetch_transcript_supadata(video_id)
        print(f"Transcript for video ID {video_id}: {transcript}")
        word_count = len(transcript.split())
        print(f"Transcript word count for video ID {video_id}: {word_count}")
        if word_count > MAX_TRANSCRIPT_WORDS:
            return ErrorResponse(
                message=f"Transcript too long: {word_count} words. Max allowed is {MAX_TRANSCRIPT_WORDS}.",
                error="Transcript exceeds limit.",
                timestamp=datetime.utcnow()
            ).to_response()
        answer = ask_question_to_gemini(transcript, payload.question)
        return SuccessResponse(
            message="Answer generated successfully.",
            data={"answer": answer},
            timestamp=datetime.utcnow()
        ).to_response()

    except TranscriptsDisabled:
        return ErrorResponse(
            message="Transcripts are disabled for this video.",
            error="TranscriptsDisabled",
            timestamp=datetime.utcnow()
        ).to_response()
    except NoTranscriptFound:
        return ErrorResponse(
            message="No transcript found for this video.",
            error="NoTranscriptFound",
            timestamp=datetime.utcnow()
        ).to_response()
    except VideoUnavailable:
        return ErrorResponse(
            message="The video is unavailable or private.",
            error="VideoUnavailable",
            timestamp=datetime.utcnow()
        ).to_response()
    except CouldNotRetrieveTranscript as e:
        print(f"[DEBUG] CouldNotRetrieveTranscript for video: {video_id}, error: {str(e)}")
        return ErrorResponse(
            message="Could not retrieve the transcript due to an unknown error.",
            error="CouldNotRetrieveTranscript",
            timestamp=datetime.utcnow()
        ).to_response()
    except Exception as e:
        import traceback
        print(f"[DEBUG] Unexpected error for video: {video_id}, error: {str(e)}")
        print("[DEBUG] Traceback:", traceback.format_exc())
        return ErrorResponse(
            message="Failed to analyse video.",
            error=str(e),
            timestamp=datetime.utcnow()
        ).to_response()


def handle_youtube_analysis2(payload: YouTubeAnalysisRequest):
    url_string = str(payload.url)
    question = payload.question
    if not is_valid_youtube_url(url_string):
        return ErrorResponse(
            message="Invalid YouTube URL.",
            error="URL validation failed",
            timestamp=datetime.utcnow()
        ).to_response(status_code=400)
    else:
        print("Valid Youtube URL")
    try:
        answer = ask_question_from_youtube(url_string, question)
        return SuccessResponse(
            message="Answer generated successfully.",
            data={"answer": answer},
            timestamp=datetime.utcnow()
        ).to_response()
    except Exception as e:
        return ErrorResponse(
            message="Failed to analyse video.",
            error=str(e),
            timestamp=datetime.utcnow()
        ).to_response()
    
