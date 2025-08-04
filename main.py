from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import base64
import os
import re
import json
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Optimeleon Landing Page Generator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models

class LandingPageRequest(BaseModel):
    image_description: str
    original_headline: str
    original_subheadline: str
    marketing_insights: str

class LandingPageResponse(BaseModel):
    headline: str
    subheadline: str

# Core Analysis

class ImageAnalyzer:
    """Handles image analysis using OpenAI Vision API"""

    @staticmethod
    def analyze_image(image_bytes: bytes) -> str:
        """Analyze image and extract key visual themes, emotions, and messages"""
        try:
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Analyze this advertisement image and extract:\n"
                                    "1. Key visual themes and elements\n"
                                    "2. Emotional tone and mood\n"
                                    "3. Target audience implied\n"
                                    "4. Main message or call to action\n"
                                    "5. Colors, composition, and style\n\n"
                                    "Provide a detailed description that can be used for personalized marketing content generation."
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            return response.choices[0].message.content

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image analysis failed: {e}")

# Core Content gen
def clean_code_block(text: str) -> str:
    """
    Removes markdown-style triple backticks and surrounding whitespace.
    """
    if text.startswith("```") and text.endswith("```"):
        return text.strip("`").strip()
    return text.strip("`").strip()

class ContentGenerator:
    """Handles personalized content generation"""

    @staticmethod
    def generate_personalized_content(image_analysis: str, original_headline: str, original_subheadline: str, marketing_insights: str) -> Dict[str, str]:
        """Generate personalized headline and subheadline"""

        prompt = (
            f"You are a marketing copywriter. Based on the following:\n\n"
            f"IMAGE ANALYSIS:\n{image_analysis}\n\n"
            f"MARKETING INSIGHTS:\n{marketing_insights}\n\n"
            f"The user has provided this HEADLINE HTML structure:\n{original_headline}\n\n"
            f"And this SUBHEADLINE HTML structure:\n{original_subheadline}\n\n"
            "Extract only the visible *text content* from each HTML structure, then rewrite it to be more compelling, emotionally resonant, and conversion-optimized, while preserving the same structure, length, and tone.\n\n"
            "Return only a valid JSON object in the following format:\n"
            "{\n"
            '  "headline": "<h1>...updated HTML...</h1>",\n'
            '  "subheadline": "<p>...updated HTML...</p>"\n'
            "}\n"
            "Do NOT include any markdown formatting, backticks, or explanation text—only valid JSON."
        )

        try:
            resp = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert e-commerce copywriter."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            resp_text = resp.choices[0].message.content.strip()
            parsed = json.loads(resp_text)

            return {
                "headline": parsed.get("headline", "").strip(),
                "subheadline": parsed.get("subheadline", "").strip()
            }

        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse JSON from LLM: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Content generation failed: {e}")

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Optimeleon Landing Page Generator API is up."}

@app.post("/analyze-image")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    img_bytes = await file.read()
    desc = ImageAnalyzer.analyze_image(img_bytes)
    return {"image_description": desc}

@app.post("/generate-content", response_model=LandingPageResponse)
async def generate_content(request: LandingPageRequest):
    out = ContentGenerator.generate_personalized_content(
        request.image_description,
        request.original_headline,
        request.original_subheadline,
        request.marketing_insights
    )
    return LandingPageResponse(**out)

@app.post("/generate-from-image")
async def generate_from_image(file: UploadFile = File(...), original_headline: str = "", original_subheadline: str = "", marketing_insights: str = ""):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    img_bytes = await file.read()
    img_desc = ImageAnalyzer.analyze_image(img_bytes)
    out = ContentGenerator.generate_personalized_content(img_desc, original_headline, original_subheadline, marketing_insights)
    return {"image_analysis": img_desc, **out}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)