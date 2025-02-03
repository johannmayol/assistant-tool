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

@app.post("/read_file/")
async def read_file(file_path: str):
    """ Lit un fichier et retourne son contenu. """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@app.post("/run_command/")
async def run_command(command: str):
    """ Exécute une commande sur le PC (attention à la sécurité). """
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return {"output": result.stdout, "error": result.stderr}

@app.get("/status")
async def get_status():
    return {"status": "Tout fonctionne correctement !"}


class SearchRequest(BaseModel):
    query: str

@app.post("/search_web/")
async def search_web(request: SearchRequest):
    """ Effectue une recherche sur le web et retourne les premiers résultats. """
    try:
        search_url = f"https://api.duckduckgo.com/?q={request.query}&format=json"
        response = requests.get(search_url)
        data = response.json()
        
        # Extraire les premiers résultats
        results = [
            {"title": item["Text"], "url": item["FirstURL"]}
            for item in data.get("RelatedTopics", [])
            if "Text" in item and "FirstURL" in item
        ]

        return {"results": results[:5]}  # Limite à 5 résultats
    except Exception as e:
        return {"error": str(e)}