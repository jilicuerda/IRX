import streamlit as st
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
# On importe les fonctions de calcul depuis votre autre fichier
import process_image as proc 

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="iRX Web Analysis", layout="wide")

# --- STYLE ROUGE & BLANC ---
plt.style.use('default')
mpl.rcParams.update({
    'axes.edgecolor': '#b30000',
    'grid.color': '#b30000',
    'grid.alpha': 0.2,
    'lines.color': '#cc0000',
    'axes.labelcolor': 'black'
})

st.title("🔬 iRX Image Analysis Dashboard")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Paramètres")
    mu_value = st.number_input("Valeur de mu (cm-1)", value=0.20)
    
    st.divider()
    st.header("📂 Chargement")
    file_dry = st.file_uploader("Image DRY (TIFF)", type=["tif", "tiff"])
    file_wet = st.file_uploader("Image WET (TIFF)", type=["tif", "tiff"])
    
    compute_btn = st.button("🚀 Lancer l'analyse", type="primary", use_container_width=True)

# --- ZONE D'AFFICHAGE ---
if compute_btn and file_dry and file_wet:
    with st.spinner("Calculs en cours..."):
        # 1. Lecture des images via process_image
        img_dry = proc.read_tiff(file_dry)
        img_wet = proc.read_tiff(file_wet)
        
        # 2. Calcul simple (exemple)
        diff = img_wet - img_dry
        
        # 3. Affichage des résultats
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Image de différence")
            fig1, ax1 = plt.subplots()
            im = ax1.imshow(diff, cmap='Reds')
            plt.colorbar(im, ax=ax1)
            st.pyplot(fig1)
            
        with col2:
            st.subheader("Profil Horizontal")
            fig2, ax2 = plt.subplots()
            ax2.plot(diff[diff.shape[0]//2, :]) # Profil au milieu
            ax2.grid(True)
            st.pyplot(fig2)
else:
    st.info("Veuillez charger les images Dry et Wet à gauche pour commencer.")
