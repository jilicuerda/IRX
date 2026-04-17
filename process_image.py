import numpy as np
import tifffile as tiff

def read_tiff(uploaded_file):
    """
    Lit un fichier TIFF chargé depuis l'interface Streamlit (en mémoire)
    et le convertit en matrice Numpy 32 bits (float32).
    """
    try:
        # Streamlit envoie un flux de données (BytesIO), tifffile sait le lire nativement
        img = tiff.imread(uploaded_file)
        
        # On force en float32 pour l'optimisation de la mémoire et des calculs
        return img.astype(np.float32)
    
    except Exception as e:
        print(f"Erreur lors de la lecture de l'image : {e}")
        # En cas d'erreur (fichier corrompu, etc.), on renvoie une matrice vide
        # Cela évite que le serveur web ne crashe complètement.
        return np.zeros((100, 100), dtype=np.float32)


def compute_mu(image_dry, image_wet, diameter):
    """
    Calcule le coefficient d'atténuation (mu).
    """
    # Sécurité mathématique : on remplace les 0 par une valeur minuscule 
    # pour éviter que la division et le logarithme ne fassent crasher Python
    safe_wet = np.where(image_wet == 0, 1e-6, image_wet)
    safe_dry = np.where(image_dry == 0, 1e-6, image_dry)
    
    # Calcul de la formule physique, forcé en float32
    mu = (-np.log(safe_dry / safe_wet) / diameter).astype(np.float32)
    
    return mu


def compute_porosity(mu_array, mu_ref_dry, mu_ref_wet):
    """
    Exemple de structure pour le calcul de la porosité (Phi.L).
    """
    diff_ref = mu_ref_wet - mu_ref_dry
    if diff_ref == 0:
        diff_ref = 1e-6 # Sécurité division par zéro
        
    phi_l = ((mu_array - mu_ref_dry) / diff_ref).astype(np.float32)
    return phi_l

# -------------------------------------------------------------------
# VOUS POUVEZ COLLER LE RESTE DE VOS FORMULES MATHÉMATIQUES ICI
# (Saturations 2-phases, Saturations 3-phases, etc.)
# 
# Règle d'or : Utilisez uniquement du code Numpy pur.
# Ne remettez JAMAIS de 'from PySide6' ou 'import tkinter' dans ce fichier !
# -------------------------------------------------------------------
