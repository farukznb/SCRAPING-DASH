import streamlit as st
import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
import base64

# Fonction de scraping
def scrape_multiple_pages(base_url, last_page_index):
    all_data = []
    for page_index in range(1, last_page_index + 1):
        print(f"Scraping page {page_index}...")
        url = f'{base_url}&nb={page_index}'
        page = get(url)
        ps = bs(page.text, 'html.parser')
        containers = ps.find_all('div', class_='item-inner mv-effect-translate-1 mv-box-shadow-gray-1')

        for container in containers:
            try:
                link = container.find('a')['href']
                res_c = get(link)
                soup_c = bs(res_c.text, 'html.parser')
                
                brand = soup_c.find('a', class_='mv-overflow-ellipsis').text
                price = soup_c.find('span', class_='new-price').text.strip().replace('.', '').replace('FCFA', '').replace(' ', '')
                add = soup_c.find('div', class_="block-27-desc")
                address = ' '.join(part for part in add.stripped_strings).split('/')
                address_ = address[1]
                image = soup_c.find('div', class_='slick-slide-inner mv-box-shadow-gray-2').img['src']
                image_link = "https://dakarvente.com/" + image
                
                dic = {'Brand': brand, 'Price': price, 'Address': address_, 'Image link': image_link}
                all_data.append(dic)
            except Exception as e:
                print(f"Error scraping a container on page {page_index}: {e}")
                continue
    
    df = pd.DataFrame(all_data)
    return df

# Streamlit app
st.title("Dashboard Basique avec Streamlit")

# Appliquer du CSS pour personnaliser le design
# Fonction pour intégrer une image locale dans le style CSS
def local_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode()
    return base64_image

# Spécifiez le chemin de l'image
image_path = "C:/Users/GENERAL STORES/Documents/GitHub/Dash/back.jpg"
base64_image = local_image_to_base64(image_path)

# Intégrer l'image dans le CSS
st.markdown(
    f"""
    <style>
    body {{
        background: url('data:image/jpg;base64,{base64_image}') no-repeat center center fixed;
        background-size: cover;
        font-family: Arial, sans-serif;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for user input features
st.sidebar.header("User Input Features")

# Example base URLs for scraping
example_sites = {
    "Vehicules": "https://dakarvente.com/index.php?page=annonces_rubrique&url_categorie_2=vehicules&id=2&sort=",
    "Motos": "https://dakarvente.com/index.php?page=annonces_categorie&id=3&sort=",
    "Location": "https://dakarvente.com/index.php?page=annonces_categorie&id=8&sort=",
    "Telephones": "https://dakarvente.com/index.php?page=annonces_categorie&id=32&sort="
}

# Last page index for each site
last_page_indices = {
    "Vehicules": 129,
    "Motos": 5,
    "Location": 12,
    "Telephones": 46 
}

# Options for the main actions
options = ["Fill the Form", "Scrape Data Using BeautifulSoup", "Download Scraped Data", "Dashboard of the Data"]
selected_option = st.sidebar.selectbox("Choisissez une option :", options)

# Logic for the "Fill the Form" option
if selected_option == "Fill the Form":
    st.subheader("Formulaire KoboToolbox")
    # Embed the KoboToolbox form using an iframe
    form_url = "https://ee.kobotoolbox.org/i/pMw5itNC"
    st.components.v1.iframe(src=form_url, width=800, height=600)

# Logic for scraping data when the option is selected
elif selected_option == "Scrape Data Using BeautifulSoup":
    selected_site = st.sidebar.selectbox("Choisissez un site à scraper :", list(example_sites.keys()))
    base_url = example_sites[selected_site]
    last_page_index = last_page_indices[selected_site]
    nombre_de_pages = st.sidebar.selectbox("Nombre de pages à scraper", options=range(1, last_page_index + 1), index=4)

    if st.button("Commencer le scraping"):
        result = scrape_multiple_pages(base_url, nombre_de_pages)
        st.subheader("Données Scrappées")
        st.write(result)

        # Optionally display statistics
        st.subheader("Statistiques")
        st.write("Nombre d'éléments scrappés :", len(result))

        # Download buttons
        csv = result.to_csv(index=False).encode('utf-8')
        st.download_button(label="Télécharger en CSV",
                           data=csv,
                           file_name='data.csv',
                           mime='text/csv')