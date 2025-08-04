# Opti: Ad Image Analyzer & Webpage Headline Generation Tool
## Purpose
Analyzes advertisement images and generates personalized, conversion-optimized headlines and subheadlines based on marketing insights.

## Features
- Image Analysis: Uses GPT-4o-mini with vision to extract visual themes, emotions, and text messages
- Text Generation: Leverages GPT-4 to create compelling, personalized details
- Marketing Personalization: Tailors content based on target audience, pain points, and product features
- Production-Ready API: FastAPI backend with comprehensive endpoints

---
## Project Structure
```
├── compose.yaml
├── Dockerfile
├── generated_preview.html
├── main.py                 # FastAPI backend entrypoint
├── README.Docker.md
├── README.md
├── requirements.txt
└── st_app.py               # Streamlit frontend app
```

## Infering APIs

1. POST `/analyze-image`

Upload an image and metadata to generate ad copy.

**Request**:
- image: Upload file (.jpg, .png, etc)

**Response**:
```json
{
  "image_description": "A high performance running shoe placed on a track, bathed in dramatic lighting suggesting speed and innovation."
}
```

2. POST `/generate-content`

Generates personalized headline and subheadline using an image description, original copy, and marketing insights.

**Request**:
```json
{
  "image_description": "Elite road running shoes under stadium lights.",
  "original_headline": "Built for Speed",
  "original_subheadline": "Nike Vaporfly 3 empowers runners with next-gen energy return.",
  "marketing_insights": "Pain point: inconsistency in cushioning; Feature: cushioned foam; Audience: elite marathoners"
}
```

**Response**:
```json
{
  "headline": "",
  "subheadline": ""
}
```

---
## Setup

1. Clone the repo
```bash
git clone https://github.com/sree-sphere/Opti.git
cd Opti
```

2. Setup env `OPENAI_API_KEY`

3. Build and Run
- Option A: Docker

    `docker compose up --build`
- Option B: local

    `uvicorn main:app --reload`
    `streamlit run st_app.py`

4. Tests
- `PYTHONPATH=. pytest --cov=src --cov-report=term-missing --cov-report=html`

---

## Notes

### Justifications
- OpenAI (vision) vs Hugging Face models/spaces: Quick, easy to control, reliable over validity as the code aims to be modular and easy to replace anyways. I have used CLIP models before but they're not very accurate so research would cost me time.
- OpenAI vs Groq/OpenRouter: latest gpt models are quite valid than open source, and given time I cannot hit a rate limit at rush hour.

### Challenges
- Not much time put in to searching HuggingFace alternatives
- Not much testing on how far visual semantics were extracted
- Placeholders for PDF parsing
- HTML rendering on Streamlit
- python-multipart installation for Docker

### Improvements
- Multilingual support
- Batch uploades and bulk content generation
- Fine-tuning responses
- A/B testing prompts