import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# Importation de votre fichier de calculs mathématiques
import process_image as proc 

# --- 1. CONFIGURATION DE LA PAGE ---
# On force l'affichage en mode large (Dashboard)
st.set_page_config(page_title="iRX Dashboard", page_icon="🔴", layout="wide")

# --- 2. STYLE MATPLOTLIB (Rouge et Blanc) ---
plt.style.use('default')
mpl.rcParams.update({
    'axes.edgecolor': '#b30000',    # Bordures rouges
    'axes.linewidth': 1.5,
    'grid.color': '#b30000',        # Grilles rouges
    'grid.alpha': 0.3,              # Transparence des grilles
    'lines.color': '#cc0000',       # Courbes en rouge vif
    'lines.linewidth': 2.0,
    'xtick.color': 'black',
    'ytick.color': 'black',
    'axes.labelcolor': 'black',
    'figure.facecolor': 'white',    # Fond blanc garanti
    'axes.facecolor': 'white'
})

# Titre principal
st.title("🔬 Professional X-Ray Image Analysis Dashboard")

# --- 3. BARRE LATÉRALE (Inputs & Uploads) ---
with st.sidebar:
    st.header("⚙️ Input Parameters")
    rotation = st.number_input("Rotation Angle (degrees)", value=90.0)
    mult_core = st.number_input("Multiply core image by", value=1.0)
    mult_time = st.number_input("Multiply time reference window by", value=1.0)
    
    st.divider() # Ligne de séparation
    
    st.header("📂 Image Phases")
    # Zones de glisser-déposer pour les images TIFF
    images_1p = st.file_uploader("1-Phase Images (ex: Dry / Wet)", type=["tif", "tiff"], accept_multiple_files=True)
    images_2p = st.file_uploader("2-Phases Images", type=["tif", "tiff"], accept_multiple_files=True)
    images_3p = st.file_uploader("3-Phases Images", type=["tif", "tiff"], accept_multiple_files=True)
    
    st.divider()
    
    # Bouton d'action principal
    compute_btn = st.button("🚀 Perform Analysis & Update", use_container_width=True, type="primary")


# --- 4. ZONE PRINCIPALE (Graphiques et Calculs) ---

# Si l'utilisateur a cliqué sur le bouton ET qu'il a mis des images
if compute_btn:
    if images_1p and len(images_1p) >= 1:
        with st.spinner("Processing X-Ray Data... Please wait"):
            
            # ---------------------------------------------------------
            # VRAIS CALCULS (À lier avec vos fonctions proc.xxx plus tard)
            # Exemple : 
            # image_data = proc.read_tiff(images_1p[0])
            # ---------------------------------------------------------
            
            # --- Graphique 1 : Core Image (Large) ---
            st.subheader("Core Image")
            fig_img, ax_img = plt.subplots(figsize=(15, 3))
            
            # Remplacer np.random.rand par votre vraie image calculée
            # cmap='Reds' donne le look rouge médical à l'image radio
            ax_img.imshow(np.random.rand(100, 800), cmap='Reds', aspect='auto') 
            ax_img.set_ylabel("core length (pixels)")
            ax_img.set_xlabel("core length (pixels)")
            
            # Affichage du graphique dans Streamlit (Remplace FigureCanvas)
            st.pyplot(fig_img)

            # --- Séparation en 2 colonnes pour les graphiques du bas ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Core Profile (ADU)")
                fig_prof, ax_prof = plt.subplots()
                
                # Remplacer par votre vrai profil
                x = np.linspace(-0.05, 0.05, 100)
                y = np.abs(np.sin(x * 50)) + np.random.normal(0, 0.1, 100) 
                
                ax_prof.plot(x, y)
                ax_prof.grid(True)
                st.pyplot(fig_prof)
                
            with col2:
                st.subheader("Histogram inside cale de mu")
                fig_hist, ax_hist = plt.subplots()
                
                # Remplacer par vos vraies données d'histogramme
                data = np.random.normal(0, 0.01, 1000)
                
                ax_hist.hist(data, bins=50, color='#cc0000', alpha=0.7)
                ax_hist.grid(True)
                st.pyplot(fig_hist)
                
    else:
        # Avertissement si on clique sur le bouton sans charger d'images
        st.warning("⚠️ Veuillez charger au moins une image dans '1-Phase Images' pour lancer le test.")

else:
    # Message d'accueil par défaut
    st.info("👈 Veuillez paramétrer votre analyse et charger vos images dans le menu de gauche, puis cliquez sur 'Perform Analysis'.")
