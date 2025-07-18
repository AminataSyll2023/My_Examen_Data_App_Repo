import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import base64
import re
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration de la page
st.set_page_config(
    page_title="MY DATA SCRAPER APP",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour l'interface
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .description {
        text-align: center;
        color: #5d6d7e;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #5a67d8, #6b46c1);
        transform: translateY(-2px);
    }
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">MY DATA SCRAPER APP</h1>', unsafe_allow_html=True)
st.markdown('<p class="description">Cette app permet de scraper des données depuis des sites web sur plusieurs pages. Vous pouvez aussi télécharger des fichiers CSV préexistants.</p>', unsafe_allow_html=True)

# Sidebar - User Input Features
st.sidebar.header("🔧 User Input Features")

# Pages indexes
st.sidebar.subheader("Pages à scraper")
pages_option = st.sidebar.selectbox(
    "Nombre de pages à scraper",
    [1, 2, 3, 4, 5, 10, 20, 50, 100],
    index=1
)

# Options de scraping
st.sidebar.subheader("Options")
scraping_method = st.sidebar.selectbox(
    "Méthode",
    ["Scrape data using BeautifulSoup", "Download scraped data", "Dashboard", "Fill the form"]
)

# Catégorie
st.sidebar.subheader("Catégorie")
category_option = st.sidebar.selectbox(
    "Choisissez la catégorie",
    ["Villas", "Terrains", "Appartements"],
    index=0
)

# Bouton d'action
st.sidebar.subheader("Actions")
download_clicked = False
scrape_clicked = False

if scraping_method == "Scrape data using BeautifulSoup":
    if st.sidebar.button("Scraper"):
        scrape_clicked = True

elif scraping_method == "Download scraped data":
    if st.sidebar.button("Télécharger"):
        download_clicked = True



# Fonctions de scraping
def scrape_villas(pages):
    df = pd.DataFrame()
    for p in range(1, pages + 1):
        url = f'https://sn.coinafrique.com/categorie/villas?page={p}'
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')

        data = []
        for c in containers:
            try:
                desc = c.find('p', class_='ad__card-description').text.strip()
                type_annonce = desc.split()[0]

                # Extraire un nombre uniquement depuis la description
                match = re.search(r'\b(\d+)\b', desc)
                nombre_pieces = match.group(1) if match else ''

                prix = c.find('p', class_='ad__card-price').text.replace('CFA', '').strip()
                adresse = " ".join(c.find('p', 'ad__card-location').text.split()[2:4])
                image_lien = c.find('img', 'ad__card-img')['src']

                data.append({
                    'page': p,
                    'type_annonce': type_annonce,
                    'nombre_pieces': nombre_pieces,
                    'prix': prix,
                    'adresse': adresse,
                    'image_lien': image_lien
                })
            except:
                pass
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    return df

def scrape_terrains(pages):
    df = pd.DataFrame()
    for p in range(1, pages + 1):
        url = f'https://sn.coinafrique.com/categorie/terrains?page={p}'
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')

        data = []
        for c in containers:
            try:
                desc = c.find('p', class_='ad__card-description').text.strip()

                # Extraire uniquement les chiffres avec . ou , (ex: 400, 1.5 etc.)
                superficie_match = re.search(r"[\d.,]+", desc)
                superficie = superficie_match.group().replace(",", "") if superficie_match else None

                prix = c.find('p', 'ad__card-price').text.replace('CFA', '').strip()
                adresse = " ".join(c.find('p', 'ad__card-location').text.split()[2:4])
                image_lien = c.find('img', 'ad__card-img')['src']
                data.append({
                    'page': p,
                    'superficie': superficie,
                    'prix': prix,
                    'adresse': adresse,
                    'image_lien': image_lien
                })
            except:
                pass
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    return df

def scrape_appartements(pages):
    df = pd.DataFrame()
    for p in range(1, pages + 1):
        url = f'https://sn.coinafrique.com/categorie/appartements?page={p}'
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        containers = soup.find_all('div', class_='col s6 m4 l3')

        data = []
        for c in containers:
            try:
                desc = c.find('p', 'ad__card-description').text.strip()
                # Extraire un nombre uniquement depuis la description
                match = re.search(r'\b(\d+)\b', desc)
                nombre_pieces = match.group(1) if match else ''
                prix = c.find('p', class_='ad__card-price').text.replace('CFA', '').strip()
                adresse = " ".join(c.find('p', 'ad__card-location').text.split()[2:4])
                image_lien = c.find('img', 'ad__card-img')['src']
                data.append({
                    'page': p,
                    'nombre_pieces': nombre_pieces,
                    'prix': prix,
                    'adresse': adresse,
                    'image_lien': image_lien
                })
            except:
                pass
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    return df

# Centralisation des chemins CSV
file_paths = {
    "Villas": r"C:\Users\admin\Desktop\DIT\Data callection\EXAM\CoinAfrique_villas_sitemap.csv",
    "Terrains": r"C:\Users\admin\Desktop\DIT\Data callection\EXAM\CoinAfrique_terrains_sitemap.csv",
    "Appartements": r"C:\Users\admin\Desktop\DIT\Data callection\EXAM\CoinAfrique_appartements_sitemap.csv",
}

# Fonction pour générer un lien de téléchargement CSV
def get_csv_download_link(df, filename="data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # encode to base64
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Cliquez ici pour télécharger {filename}</a>'
    return href

# Gestion du scraping
if scrape_clicked:
    with st.spinner(f"Scraping {category_option} en cours sur {pages_option} page(s)..."):
        if category_option == "Villas":
            df_scraped = scrape_villas(pages_option)
        elif category_option == "Terrains":
            df_scraped = scrape_terrains(pages_option)
        else:
            df_scraped = scrape_appartements(pages_option)

    if df_scraped.empty:
        st.error("Aucune donnée trouvée lors du scraping.")
    else:
        st.success(f"Scraping terminé : {len(df_scraped)} annonces récupérées.")
        st.dataframe(df_scraped, use_container_width=True)
        st.session_state['scraped_data'] = df_scraped

        # Sauvegarde automatique du fichier après scraping
        save_path = file_paths.get(category_option)
        if save_path:
            try:
                df_scraped.to_csv(save_path, index=False)
                st.info(f"Données sauvegardées dans : {save_path}")
            except Exception as e:
                st.error(f"Erreur lors de la sauvegarde des données : {e}")

# Gestion du téléchargement
if download_clicked:
    file_path = file_paths.get(category_option)

    if file_path and os.path.exists(file_path):
        try:
            df_local = pd.read_csv(file_path)
            st.write(f"Fichier chargé : {file_path}")
            st.dataframe(df_local, use_container_width=True)
            tmp_download_link = get_csv_download_link(df_local, filename=f"{category_option}.csv")
            st.markdown(tmp_download_link, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier local : {e}")
    else:
        st.error("Le fichier local n'existe pas.")

# Dashboard
if scraping_method == "Dashboard":
    st.subheader(" Dashboard")

    file_path = file_paths.get(category_option)

    if file_path and os.path.exists(file_path):
        try:
            df_dashboard = pd.read_csv(file_path)
            st.success(f"Données chargées depuis le fichier : {file_path}")

            st.markdown("### Aperçu des données")
            st.dataframe(df_dashboard.head(), use_container_width=True)

            # Nettoyage
            df_dashboard["prix"] = pd.to_numeric(df_dashboard["prix"].str.replace(r"[^\d]", "", regex=True), errors='coerce')
            df_dashboard.dropna(subset=["prix"], inplace=True)

            # KPIs
            st.markdown("###  Statistiques clés")
            col1, col2 = st.columns(2)
            col1.metric("Nombre d'annonces", len(df_dashboard))
            col2.metric("Prix moyen", f"{int(df_dashboard['prix'].mean()):,} CFA")

            # Visualisations
            st.markdown("### Graphiques")

            if category_option in ["Appartements", "Villas"]:
                if "nombre_pieces" in df_dashboard.columns:
                    fig1, ax1 = plt.subplots()
                    sns.countplot(data=df_dashboard, x="nombre_pieces", ax=ax1, palette="viridis")
                    ax1.set_title("Nombre d'annonces par nombre de pièces")
                    st.pyplot(fig1)

            if "adresse" in df_dashboard.columns:
                top_villes = df_dashboard["adresse"].value_counts().nlargest(10)
                fig2, ax2 = plt.subplots()
                top_villes.plot(kind='barh', ax=ax2, color='skyblue')
                ax2.set_title("Top 10 des localisations")
                st.pyplot(fig2)

            fig3, ax3 = plt.subplots()
            sns.histplot(df_dashboard["prix"], bins=30, kde=True, ax=ax3, color='orange')
            ax3.set_title("Distribution des prix")
            st.pyplot(fig3)

        except Exception as e:
            st.error(f"Aucune donnée disponible pour le dashboard. Erreur : {e}")
    else:
        st.error("Le fichier de données pour le dashboard n'existe pas.")

# Affichage du formulaire si l'utilisateur sélectionne "Fill the form"
if scraping_method == "Fill the form":
    st.subheader(" Formulaire d’évaluation de l’application")
    st.markdown("Merci de prendre un moment pour évaluer cette application. Vos retours nous aident à l’améliorer.")

    st.markdown(
        """
        <iframe src="https://ee.kobotoolbox.org/i/0qn8TxTG" width="100%" height="600" style="border:none;"></iframe>
        """,
        unsafe_allow_html=True
    )

# Footer
st.markdown("---")
st.markdown("** **")
