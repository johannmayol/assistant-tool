import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import logging
import subprocess

# Initialisation de l'application FastAPI
app = FastAPI()

# Activer CORS pour que le frontend puisse interagir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Variables d'environnement
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MISTRAL_SYSTEM_PROMPT = os.getenv("MISTRAL_SYSTEM_PROMPT", "Tu es un assistant francophone. Réponds uniquement en français.")

# 🔹 Orchestrateur IA : Définition des sous-agents
AGENT_URLS = {
    "génération de texte": os.getenv("TEXT_GEN_URL", "http://backend:8001/generate"),
    "résumé": os.getenv("SUMMARY_URL", "http://backend:8002/summarize"),
}

# 📌 1️⃣ **Endpoint `/` pour vérifier que le backend fonctionne**
@app.get("/")
async def read_root():
    return {"message": "Bonjour, l'assistant est en ligne !"}

# 📌 2️⃣ **Endpoint `/ask_mistral/` pour interagir avec Mistral 7B**
class PromptRequest(BaseModel):
    prompt: str

@app.post("/ask_mistral/")
async def ask_mistral(request: PromptRequest):
    """ Envoie une requête à Mistral 7B via Ollama """
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
        return {"response": response_data.get("response", "Pas de réponse générée.")}
    except Exception as e:
        return {"error": str(e)}

# 📌 3️⃣ **Endpoint `/dispatch/` pour l’orchestrateur IA (ajouté)**
class RequestPayload(BaseModel):
    task: str
    input_data: str

@app.post("/dispatch/")
async def dispatch_task(payload: RequestPayload):
    """ Oriente la requête vers le bon sous-agent (génération de texte, résumé, etc.) """
    agent_url = AGENT_URLS.get(payload.task)
    
    if not agent_url:
        logging.error(f"Tâche inconnue: {payload.task}")
        raise HTTPException(status_code=400, detail="Tâche non reconnue")

    logging.info(f"Redirection vers {agent_url} pour la tâche: {payload.task}")

    try:
        response = requests.post(agent_url, json={"input_data": payload.input_data})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Erreur de l'agent: {e}")
        raise HTTPException(status_code=500, detail="Erreur de l'agent")

# 📌 4️⃣ **Endpoint `/read_file/` pour lire un fichier**
@app.post("/read_file/")
async def read_file(file_path: str):
    """ Lit un fichier et retourne son contenu. """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

# 📌 5️⃣ **Endpoint `/run_command/` pour exécuter une commande**
@app.post("/run_command/")
async def run_command(command: str):
    """ Exécute une commande sur le PC (attention à la sécurité). """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return {"output": result.stdout, "error": result.stderr}

# 📌 6️⃣ **Endpoint `/status/` pour vérifier l'état du backend**
@app.get("/status/")
async def get_status():
    return {"status": "Tout fonctionne correctement !"}

# 📌 7️⃣ **Endpoint `/search_web/` pour une recherche web**
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

