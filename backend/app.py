import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI()

# Activer CORS pour que le frontend puisse interagir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Récupérer l'URL d'Ollama définie dans `docker-compose.yml`
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MISTRAL_SYSTEM_PROMPT = os.getenv("MISTRAL_SYSTEM_PROMPT", "Tu es un assistant francophone. Réponds uniquement en français.")

@app.get("/")
async def read_root():
    return {"message": "Bonjour, l'assistant est en ligne !"}


class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask_mistral/")
async def ask_mistral(request: PromptRequest):
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": "mistral",
                "prompt": f"{MISTRAL_SYSTEM_PROMPT}\n\nQuestion : {request.prompt}\n\nRéponse :",
                "stream": False
            }
        )
        response_data = response.json()
        print(response_data) #temporaire
        return {"response": response_data.get("response", "Pas de réponse générée.")}
    except Exception as e:
        return {"error": str(e)}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Bonjour, {name} !"}

@app.get("/status")
async def get_status():
    return {"status": "Tout fonctionne correctement !"}
