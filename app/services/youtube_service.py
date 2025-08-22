from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai  # Corrected import
import os
from supadata import Supadata



from dotenv import load_dotenv
load_dotenv()



API_KEY = os.getenv("GEMINI_API_KEY")
SUPADATA_KEY = os.getenv("SUPADATA_KEY")


if API_KEY:
    genai.configure(api_key=API_KEY)
    print("Gemini API key configured successfully.")
else:
    print("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")

supadata = Supadata(api_key=SUPADATA_KEY)


def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    print(f"Video ID query parameters: {parsed_url}")
    # Case 1: Short URL (youtu.be/<video_id>)
    if parsed_url.netloc == "youtu.be":
        return parsed_url.path[1:]  # remove leading '/'
    # Case 2: Standard URL (youtube.com/watch?v=<video_id>)
    query = parse_qs(parsed_url.query)
    return query.get("v", [None])[0]



def fetch_transcript(video_id: str) -> str:
    yt_api = YouTubeTranscriptApi()  # instantiate the class
    transcript = yt_api.fetch(video_id, languages=["en"])
    transcript_text = " ".join([snippet.text for snippet in transcript])
    print(f"Fetched transcript for video ID {video_id}: {transcript_text[:100]}...")  # Log first 100 characters
    return transcript_text


def fetch_transcript_supadata(video_id: str) -> str:
    try:
        response = supadata.youtube.transcript(video_id=video_id, text=True)
        
        if not response or not hasattr(response, "content") or not response.content:
            raise ValueError("Transcript content is empty or unavailable")

        transcript_text = response.content
        # print(f"[DEBUG] Fetched transcript for {video_id}: {transcript_text}")

        return transcript_text

    except Exception as e:
        print(f"[DEBUG] Supadata transcript fetch failed for {video_id}: {str(e)}")
        raise RuntimeError(f"Failed to fetch transcript: {str(e)}")




def ask_question_to_gemini(transcript: str, question: str) -> str:
    SYSTEM_PROMPT = """
You are YT-Sage, an AI assistant that analyzes YouTube videos using the provided transcript.

Your responsibilities:
1. Only answer questions using the information in the transcript.
2. If the question is not relevant to the transcript, say:
   "YT-Sage cannot answer this question as it is not relevant to the content of this video."
3. If the user asks for explanation or clarification (a doubt), explain it properly using transcript content and general knowledge — but clearly mention when you're adding additional context.
4. If the user specifies a format like "in 100 words" or "in 5 lines", follow that strictly.
5. Guidelines for tone and clarity:
   - Be clear, simple, and easy to understand.
   - Avoid technical jargon unless the transcript contains it.
   - If the question is short and simple, respond concisely in 3-4 lines.
   - If the question is detailed or asks for explanation, provide a brief but complete answer (maximum three paragraphs or 4000 words).
   - Never hallucinate or invent details not present or inferable from the transcript.
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"{SYSTEM_PROMPT}\n\nTranscript:\n{transcript}\n\nQuestion: {question}"
    
    response = model.generate_content(prompt)
    return response.text


def ask_question_from_youtube(video_url: str, question: str) -> str:
    SYSTEM_PROMPT = """
You are YT-Sage, an AI assistant that analyzes YouTube videos.

Rules:
1. Use the Youtube video link provided get the transcript from this video and understand the content.
2. Only answer questions that are relevant to the video transcript.
3. If irrelevant, say: "YT-Sage cannot answer this question as it is not relevant to the content of this video."
4. Be simple, clear, and accurate. No hallucinations.
"""

    model = genai.GenerativeModel("gemini-2.0-flash")  # Pro supports multimodal better than flash
    prompt = f"{SYSTEM_PROMPT}\n\nVideo Url: {video_url}\n\nQuestion: {question}"

    response = model.generate_content(prompt)
    return response.text

