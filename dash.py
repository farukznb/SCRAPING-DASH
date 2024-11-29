import streamlit as st
import pandas as pd
from requests import get
from bs4 import BeautifulSoup as bs
import base64
import time  # Import time module for tracking duration
import matplotlib.pyplot as plt
import seaborn as sns


# Function to create download links
def create_download_link(df, filename_csv, filename_excel):
    # CSV download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label=f"Download {filename_csv} as CSV",
                       data=csv,
                       file_name=filename_csv,
                       mime='text/csv')
    
    # Excel download
    excel = df.to_excel(index=False, engine='openpyxl').encode('utf-8')
    st.download_button(label=f"Download {filename_excel} as Excel",
                       data=excel,
                       file_name=filename_excel,
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
   
# Function to encode the image as Base64
def local_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode()
        return base64_image
    except FileNotFoundError:
        st.error(f"Image file not found: {image_path}")
        return ""

# Apply the background image and themes using Base64
image_path = "Data/gold.jpg"
base64_image = local_image_to_base64(image_path)

if base64_image:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url('data:image/jpg;base64,{base64_image}') no-repeat center center fixed;
            background-size: cover;
            color: #FFFFFF;
        }}
        h1, h2, h3 {{
            color: #ffffff;
        }}
        .stButton>button {{
            background-color: #FF6347;
            color: #FFFFFF;
            border: none;
            padding: 10px;
            font-size: 16px;
        }}
        .stButton>button:hover {{
            background-color: #555500;
        }}
        .stSlider>div {{
            color: #FFFFFF;
        }}
        .stDataFrame {{
            background-color: rgba(0, 0, 0, 0.7);
            color: #FFFFFF;
        }}
        .title-container {{
            background-color:  #e0aa3e;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        h1.title-text {{
            color: #fffeef;
            font-size: 48px;
            font-family: 'Santa Catalina';
            font-weight: bold;
        }}
        .stSidebar {{
            background-color: #B7760B;  /* Set the sidebar background color */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Scraping function
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
st.sidebar.image("Data/logo.png", use_container_width=True)
# Streamlit app
st.markdown('<div class="title-container"><h1 class="title-text">Dakar Vente Dashboard</h1></div>', unsafe_allow_html=True)

# Sidebar for user input features
st.sidebar.header("User Input Features")

# Example base URLs for scraping
example_sites = {
    "Vehicles": "https://dakarvente.com/index.php?page=annonces_rubrique&url_categorie_2=vehicules&id=2&sort=",
    "Motorcycles": "https://dakarvente.com/index.php?page=annonces_categorie&id=3&sort=",
    "Rentals": "https://dakarvente.com/index.php?page=annonces_categorie&id=8&sort=",
    "Phones": "https://dakarvente.com/index.php?page=annonces_categorie&id=32&sort="
}

# Last page index for each site
last_page_indices = {
    "Vehicles": 129,
    "Motorcycles": 5,
    "Rentals": 12,
    "Phones": 46 
}

# Options for the main actions
options = ["Fill the Form", "Scrape Data Using BeautifulSoup", "Download Scraped Data", "Dashboard of the Data"]
selected_option = st.sidebar.selectbox("Choose an option:", options)

# Logic for the "Fill the Form" option
if selected_option == "Fill the Form":
    st.subheader("KoboToolbox Form")
    # Embed the KoboToolbox form using an iframe
    form_url = "https://ee.kobotoolbox.org/i/pMw5itNC"
    st.components.v1.iframe(src=form_url, width=800, height=600)

# Logic for scraping data when the option is selected
elif selected_option == "Scrape Data Using BeautifulSoup":
    selected_site = st.sidebar.selectbox("Choose a site to scrape:", list(example_sites.keys()))
    base_url = example_sites[selected_site]
    last_page_index = last_page_indices[selected_site]
    number_of_pages = st.sidebar.selectbox("Number of pages to scrape", options=range(1, last_page_index + 1), index=4)

    if st.button("Start scraping"):
        result = scrape_multiple_pages(base_url, number_of_pages)
        st.subheader("Scraped Data")
        st.write(result)

        # Optionally display statistics
        st.subheader("Statistics")
        st.write("Number of items scraped:", len(result))

        # Download buttons
        csv = result.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download as CSV",
                           data=csv,
                           file_name='data.csv',
                           mime='text/csv')

#  Logic for downloading pre-existing CSV files
elif selected_option == "Download Scraped Data":
    st.subheader("Download Scraped Data")
    
    # Load the CSV files
    try:
        vehicle_location = pd.read_csv('Data/location_nettoye.csv')
        vehicles_cleaned = pd.read_csv('Data/vehicules_nettoye.csv')
        motos_cleaned = pd.read_csv('Data/motos_nettoye.csv')
        phone_sales_cleaned = pd.read_csv('Data/vente_telephone_nettoye.csv')

        # Display the data before download options
        st.write("Data from rentals:")
        st.dataframe(vehicle_location)
        st.write("Data from vehicles:")
        st.dataframe(vehicles_cleaned)
        st.write("Data from Phones:")
        st.dataframe(phone_sales_cleaned)

        # Create download links for each file
        def create_download_link(df, filename):
            csv = df.to_csv(index=False)
            st.download_button(label=f"Download {filename}",
                               data=csv,
                               file_name=filename,
                               mime='text/csv')

        create_download_link(vehicle_location, 'Vehicle rental data')
        create_download_link(vehicles_cleaned, 'Vehicle data')
        create_download_link(phone_sales_cleaned, 'Phone data')
    except FileNotFoundError as e:
        st.error(f"Error: {e}. Please ensure the CSV files exist in the correct directory.")

elif selected_option == "Dashboard of the Data":
    st.subheader("Dashboard of the Data")

    def load_data():
        try:
            vehicle_location = pd.read_csv('Data/location_nettoye.csv')
            vehicles_cleaned = pd.read_csv('Data/vehicules_nettoye.csv')
            motos_cleaned = pd.read_csv('Data/motos_nettoye.csv')
            phone_sales_cleaned = pd.read_csv('Data/vente_telephone_nettoye.csv')
            return vehicle_location, vehicles_cleaned, motos_cleaned, phone_sales_cleaned
        except FileNotFoundError as e:
            st.error(f"File not found: {e}")
            return None, None, None, None

    # Plotting functions
    def plot_bar(data, x, y, title, xlabel, ylabel, rotation=0, color='skyblue'):
        plt.figure(figsize=(8, 4))
        sns.barplot(data=data, x=x, y=y, color=color)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=rotation, ha='right')
        st.pyplot(plt)

    def plot_pie(data, title):
        plt.figure(figsize=(8, 6))
        data.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
        plt.title(title)
        plt.ylabel('')
        st.pyplot(plt)

    # Main logic for dashboard
    vehicle_location, vehicles_cleaned, motos_cleaned, phone_sales_cleaned = load_data()

    # Vehicles Dashboard
    if vehicles_cleaned is not None:
        st.subheader("Vehicles Dashboard")
        vehicles_cleaned['Price'] = pd.to_numeric(vehicles_cleaned['Price'], errors='coerce')

        # Brand Distribution
        
        brand_counts = vehicles_cleaned['Brand'].value_counts().head(10)
        if not brand_counts.empty:
            plot_pie(brand_counts, 'Brand Distribution - Vehicles')

        # Price Analysis by Brand
       
        if 'Brand' in vehicles_cleaned.columns and 'Price' in vehicles_cleaned.columns:
            avg_prices = vehicles_cleaned.groupby('Brand')['Price'].mean().sort_values(ascending=False).head(10).reset_index()
            avg_prices.columns = ['Brand', 'Average Price']
            plot_bar(avg_prices, 'Brand', 'Average Price', 'Average Price by Brand', 'Brand', 'Price (FCFA)', rotation=45)

    # Motorcycles Dashboard
    if motos_cleaned is not None:
        st.subheader("Motorcycles Dashboard")
        motos_cleaned['Price'] = pd.to_numeric(motos_cleaned['Price'], errors='coerce')

        # Brand Distribution
       
        brand_counts_motos = motos_cleaned['Brand'].value_counts().head(10)
        if not brand_counts_motos.empty:
            plot_pie(brand_counts_motos, 'Brand Distribution - Motorcycles')

        # Price Analysis by Brand
       
        if 'Brand' in motos_cleaned.columns and 'Price' in motos_cleaned.columns:
            avg_prices_motos = motos_cleaned.groupby('Brand')['Price'].mean().sort_values(ascending=False).head(10).reset_index()
            avg_prices_motos.columns = ['Brand', 'Average Price']
            plot_bar(avg_prices_motos, 'Brand', 'Average Price', 'Average Price by Brand - Motorcycles', 'Brand', 'Price (FCFA)', rotation=45)

    # Location Dashboard
    if vehicle_location is not None:
        st.subheader("Rentals Dashboard")
        # Brand Distribution
        st.subheader("")
        brand_counts_location = vehicle_location['Brand'].value_counts().head(10)
        if not brand_counts_location.empty:
            plot_pie(brand_counts_location, 'Brand Distribution - Rentals')

    # Phones Dashboard
    if phone_sales_cleaned is not None:
        st.subheader("Phones Dashboard")
        # Brand Distribution
        
        if 'brand' in phone_sales_cleaned.columns:
            brand_counts_phone = phone_sales_cleaned['brand'].value_counts().head(10)
            plot_pie(brand_counts_phone, 'Brand Distribution - Phones')

        # Price Analysis by Brand
       
        if 'brand' in phone_sales_cleaned.columns and 'price' in phone_sales_cleaned.columns:
            phone_sales_cleaned['price'] = pd.to_numeric(phone_sales_cleaned['price'], errors='coerce')
            avg_prices_phones = phone_sales_cleaned.groupby('brand')['price'].mean().sort_values(ascending=False).head(10).reset_index()
            avg_prices_phones.columns = ['Brand', 'Average Price']
            plot_bar(avg_prices_phones, 'Brand', 'Average Price', 'Average Price by Brand - Phones', 'Brand', 'Price (FCFA)', rotation=45)
