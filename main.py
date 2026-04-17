from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import io

# Import de votre code scientifique
import process_image as proc

app = FastAPI()

# Sécurité pour autoriser le web à discuter avec Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Quand on tape l'URL, le serveur renvoie la page HTML
@app.get("/")
async def serve_webpage():
    return FileResponse("index.html")

# 2. Quand la page web envoie les images, le serveur calcule
@app.post("/api/compute_mu")
async def compute_mu_endpoint(file_dry: UploadFile = File(...), file_wet: UploadFile = File(...)):
    try:
        # Lecture des TIFF envoyés par le web
        content_dry = await file_dry.read()
        content_wet = await file_wet.read()
        
        img_dry = proc.read_tiff(io.BytesIO(content_dry))
        img_wet = proc.read_tiff(io.BytesIO(content_wet))
        
        # --- PLACEZ VOS CALCULS ICI ---
        # Exemple simple :
        diff = img_wet - img_dry 
        
        # Préparation des données pour le JavaScript
        profil_horizontal = np.mean(diff, axis=0).tolist()
        valeur_moyenne = float(np.mean(diff))
        
        return JSONResponse(content={
            "status": "success",
            "moyenne": valeur_moyenne,
            "profil": profil_horizontal
        })
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)