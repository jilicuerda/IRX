from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
import tempfile
import shutil
import os

# Import de votre code scientifique
import process_image as proc

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. INITIALISATION DE LA MÉMOIRE ---
# On crée une instance unique de votre classe qui restera vivante sur le serveur
image_processor = proc.ProcessImage()

# On crée un dossier temporaire sur le serveur pour stocker les TIFF entrants
TEMP_DIR = tempfile.mkdtemp()

@app.get("/")
async def serve_webpage():
    return FileResponse("index.html")

# --- 2. ROUTE D'UPLOAD DES IMAGES ---
@app.post("/api/upload_images")
async def upload_images_endpoint(images_1p: List[UploadFile] = File(default=[])):
    try:
        urls = []
        for img in images_1p:
            if img.filename:
                # On sauvegarde physiquement l'image dans le dossier temporaire
                file_path = os.path.join(TEMP_DIR, img.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)
                urls.append(file_path)
        
        # On utilise votre fonction existante pour charger les images en mémoire
        # (J'ai mis 90 degrés par défaut comme dans votre interface)
        if urls:
            image_processor.load_image(angle=90.0, urls=urls)

        # On renvoie la liste des noms d'images actuellement en mémoire
        return JSONResponse(content={
            "status": "success",
            "loaded_images": list(image_processor.arrays.keys())
        })
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


# --- 3. ROUTE DU CALCUL DE MU ---
# On définit ce que le Javascript va nous envoyer
class MuRequest(BaseModel):
    name: str
    diameter: float
    dry_name: str
    fluid_name: str

@app.post("/api/compute_mu")
def compute_mu_endpoint(req: MuRequest):
    try:
        # Appel de VOTRE fonction mathématique exacte
        mu_array = image_processor.compute_mu(req.dry_name, req.fluid_name, req.diameter)
        
        # On stocke le résultat dans le dictionnaire mu_dict
        image_processor.mu_dict[req.name] = mu_array
        
        # On calcule la moyenne et l'histogramme pour le Web
        mu_avg = float(np.average(mu_array))
        hist_counts, hist_bins = np.histogram(mu_array.ravel(), bins=30)
        
        return {
            "status": "success",
            "mu_avg": mu_avg,
            "hist_counts": hist_counts.tolist(),
            "hist_bins": hist_bins.tolist()
        }
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)