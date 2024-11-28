import streamlit as st
import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
import base64
import time  # Import time module for tracking duration
import matplotlib.pyplot as plt
import seaborn as sns 

def generate_plot(data):
    # Create a scatter plot of price vs. address length
    scatter = sns.scatterplot(x="Price", y="len(Address)", data=data)
    scatter.set_title("Scatter plot of Price vs. Address Length")
    scatter.set_xlabel("Price")
    scatter.set_ylabel("Address Length")
    st.pyplot(scatter.figure)

    # Create a bar plot of the top 10 brands by price
    top_brands = data.groupby("Brand")["Price"].mean().sort_values(ascending=False).head(10)
    bar = sns.barplot(x=top_brands.index, y=top_brands.values, alpha=0.8)
    bar.set_title("Top 10 Brands by Average Price")
    bar.set_xlabel("Brand")
    bar.set_ylabel("Average Price")
    st.pyplot(bar.figure)



    # Load the CSV files
    try:
        vehicule_location = pd.read_csv('Data/location_nettoye.csv')
        vehicules_nettoye = pd.read_csv('Data/vehicules_nettoye.csv')
        vente_telephone_nettoye = pd.read_csv('Data/vente_telephone_nettoye.csv')

        # Display the data before plot options
        st.write("Data from location:")
        st.dataframe(vehicule_location)
        st.write("Data from vehicules:")
        st.dataframe(vehicules_nettoye)
        st.write("Data from Telephones:")
        st.dataframe(vente_telephone_nettoye)

        # Generate plots
        generate_plot(vehicules_nettoye)

    except FileNotFoundError as e:
        st.error(f"Error: {e}. Please ensure the CSV files exist in the correct directory.")

# Fonction de scraping
def scrape_multiple_pages(base_url, last_page_index):
    all_data = []
    start_time = time.time()  # Start timing
    for page_index in range(1, last_page_index + 1):
        st.write(f"Scraping page {page_index}...")  # Display current page being scraped
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
                all_data.append(dic)  # Append each dictionary to the list
                
            except Exception:
                continue  # Ignore errors and continue scraping
        
        # Display the number of pages scraped so far
        st.write(f"Pages already scraped: {page_index}/{last_page_index}")
    
    end_time = time.time()  # End timing
    total_time = end_time - start_time  # Calculate total time taken
    st.write(f"Total time taken for scraping: {total_time:.2f} seconds")  # Display total time taken
    
    df = pd.DataFrame(all_data)  # Convert the list of dictionaries to a DataFrame
    return df

# Streamlit app
st.title("Dashboard Basique avec Streamlit")

# Appliquer du CSS pour personnaliser le design
def local_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode()
    return base64_image

# Spécifiez le chemin de l'image
image_path = "Data/back.jpg"
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
st.sidebar.header("User    Input Features")

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
# Logic for downloading pre-existing CSV files
elif selected_option == "Download Scraped Data":
    st.subheader("Download Scraped Data")
    
    # Load the CSV files
    try:
        vehicule_location = pd.read_csv('Data/location_nettoye.csv')
        vehicules_nettoye = pd.read_csv('Data/vehicules_nettoye.csv')
        vente_telephone_nettoye = pd.read_csv('Data/vente_telephone_nettoye.csv')

        # Display the data before download options
        st.write("Data from location:")
        st.dataframe(vehicule_location)
        st.write("Data from vehicules:")
        st.dataframe(vehicules_nettoye)
        st.write("Data from Telephones:")
        st.dataframe(vente_telephone_nettoye)

        # Create download links for each file
        def create_download_link(df, filename):
            csv = df.to_csv(index=False)
            st.download_button(label=f"Download {filename }",
                               data=csv,
                               file_name=filename,
                               mime='text/csv')

        create_download_link(vehicule_location, 'Vehicules rent datas')
        create_download_link(vehicules_nettoye, 'Vehicules datas')
        create_download_link(vente_telephone_nettoye, 'Telephone datas')
    except FileNotFoundError as e:
        st.error(f"Error: {e}. Please ensure the CSV files exist in the correct directory.")

elif selected_option == "Dashboard of the Data":
    st.subheader("Dashboard of the Data")

    # Load the CSV files
try:
    vehicule_location = pd.read_csv('Data/location_nettoye.csv')
    vehicules_nettoye = pd.read_csv('Data/vehicules_nettoye.csv')
    vente_telephone_nettoye = pd.read_csv('Data/vente_telephone_nettoye.csv')

      # Generate plots

    vehicules_nettoye = pd.read_csv('Data/vehicules_nettoye.csv')
    vehicules_nettoye['Price'] = pd.to_numeric(vehicules_nettoye['Price'], errors='coerce')

   

    # 3. Marques les plus récurrentes
    st.subheader("Répartition des Marques")
    plt.figure(figsize=(10, 6))
    brand_counts = vehicules_nettoye['Brand'].value_counts().head(10)  # Top 10 marques
    brand_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('Répartition des Marques')
    plt.ylabel('')
    st.pyplot(plt)

    st.title("Analyse des Variations de Prix par Marques")

  
    # Convert Price to numeric for each dataset
    vehicule_location['Price'] = pd.to_numeric(vehicule_location['Price'], errors='coerce')
    vente_telephone_nettoye['price'] = pd.to_numeric(vente_telephone_nettoye['price'], errors='coerce')

    # 3. Marques les plus récurrentes for vehicule_location
    st.subheader("Répartition des Marques - Location")
    plt.figure(figsize=(10, 6))
    brand_counts_location = vehicule_location['Brand'].value_counts().head(10)  # Top 10 marques
    brand_counts_location.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('Répartition des Marques - Location')
    plt.ylabel('')
    st.pyplot(plt)

    # 3. Marques les plus récurrentes for vente_telephone_nettoye
    st.subheader("Répartition des Marques - Téléphones")
    plt.figure(figsize=(10, 6))
    brand_counts_telephone = vente_telephone_nettoye['brand'].value_counts().head(10)  # Top 10 marques
    brand_counts_telephone.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('Répartition des Marques - Téléphones')
    plt.ylabel('')
    st.pyplot(plt)

        
except FileNotFoundError as e:
     st.error(f"Erreur : {e}. Veuillez vérifier que le fichier existe dans le répertoire spécifié.")
