from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import numpy as np
import io

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

@app.get("/")
async def serve_webpage():
    return FileResponse("index.html")

# Nouvelle route adaptée aux Phases
@app.post("/api/process_phases")
async def process_phases_endpoint(
    # On utilise List[UploadFile] car le HTML peut envoyer plusieurs fichiers par zone.
    # Le default=[] permet de ne pas crasher si l'utilisateur laisse une zone vide.
    images_1p: List[UploadFile] = File(default=[]),
    images_2p: List[UploadFile] = File(default=[]),
    images_3pe1: List[UploadFile] = File(default=[]),
    images_3pe2: List[UploadFile] = File(default=[])
):
    try:
        # --- EXEMPLE D'UTILISATION POUR VOTRE BACKEND ---
        # 1. On initialise votre classe ProcessImage
        # image_processor = proc.ProcessImage()
        
        # 2. On lit la première image 1-Phase (si elle existe) pour l'exemple
        # if len(images_1p) > 0:
        #     content = await images_1p[0].read()
        #     img_array = proc.read_tiff(io.BytesIO(content))
        #     # Vous pouvez maintenant l'ajouter à image_processor.arrays ...
        
        
        # Pour l'instant, on renvoie simplement un accusé de réception au frontend
        # pour prouver que le câblage HTML <-> Python fonctionne parfaitement.
        return JSONResponse(content={
            "status": "success",
            "message": "Fichiers reçus et prêts pour les calculs Numpy.",
            "counts": {
                "phase1": len(images_1p),
                "phase2": len(images_2p),
                "phase3_e1": len(images_3pe1),
                "phase3_e2": len(images_3pe2)
            }
        })
        
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)