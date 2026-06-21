# Cars24 Web Scraping & Exploratory Data Analysis (EDA)

This project contains tools and analysis notebooks for scraping used car listings from [Cars24 India](https://www.cars24.com) and performing exploratory data analysis (EDA) to understand used car trends, price distributions, brand popularity, and more.

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Repository Structure](#-repository-structure)
- [Dataset Details](#-dataset-details)
- [Installation & Setup](#-installation--setup)
- [How to Run](#-how-to-run)
- [Key Insights & Visualizations](#-key-insights--visualizations)
- [Dependencies](#-dependencies)

---

## 🔍 Project Overview

The project is split into two primary workflows:
1. **Web Scraping (`Web_Scraping_Project.ipynb`)**: 
   - Dynamically scrapes pages of used car search listings from Cars24 using `requests` and `BeautifulSoup`.
   - Parses the HTML DOM to extract key attributes for each vehicle.
   - Cleans raw text data using regex (e.g., separating year and model, converting mileage strings to integers, extracting fuel and transmission tags).
   - Generates a consolidated dataset saved as `car_data.csv`.

2. **Exploratory Data Analysis (`eda_on_cars24.ipynb`)**:
   - Performs standard data validation (null values, duplicates, types).
   - Explores value distributions of final prices, odometer mileage, fuel types, and registration regions.
   - Visualizes key insights using `matplotlib` and `seaborn` such as:
     - Selling price distributions and identifying pricing outliers.
     - Average/median price distributions across vehicle manufacturers and models.
     - Price trends relative to manufacturing year.
     - Representation of fuel types (Petrol, CNG, Diesel, etc.).

---

## 📂 Repository Structure

- **[app.py](file:///c:/Users/praah/OneDrive/Documents/Coding/Cars%2024/app.py)**: Streamlit web dashboard application providing interactive visualizations and live scraping functionality.
- **[Web_Scraping_Project.ipynb](file:///c:/Users/praah/OneDrive/Documents/Coding/Cars%2024/Web_Scraping_Project.ipynb)**: Scrapes raw HTML, regularizes vehicle details, and writes the CSV dataset.
- **[car_data.csv](file:///c:/Users/praah/OneDrive/Documents/Coding/Cars%2024/car_data.csv)**: Output dataset containing details of over 1,000 listed cars.
- **[eda_on_cars24.ipynb](file:///c:/Users/praah/OneDrive/Documents/Coding/Cars%2024/eda_on_cars24.ipynb)**: Cleans, filters, processes, and visualizes the dataset to extract business patterns.
- **[requirements.txt](file:///c:/Users/praah/OneDrive/Documents/Coding/Cars%2024/requirements.txt)**: List of Python packages required to run the notebooks and Streamlit app.

---

## 📊 Dataset Details

The dataset `car_data.csv` comprises 1,009 rows with the following features:

| Column | Description | Example |
| :--- | :--- | :--- |
| **Car Name** | Year of manufacture followed by brand and model name | `2015 Hyundai Eon` |
| **Kilometers** | Total distance driven (numeric integer) | `43518` |
| **Fuel** | Fuel type configuration (Petrol, CNG, Diesel, Electric, Hybrid) | `Petrol` |
| **Transmission** | Transmission type (Manual, Automatic) | `Manual` |
| **Registration** | State code prefix of vehicle registration | `DL-11` |
| **EMI** | Monthly installment text or alternative payment detail | `EMI ₹8,826/m*` |
| **Final Price** | Stated final listing price (Indian Rupees/Lakhs) | `₹1.77 lakh` |
| **Location** | Detailed showroom location or regional branch | `M3M Urbana, Gurugram` |

---

## 🚀 Installation & Setup

To run the project locally, follow these steps:

1. **Clone or Open the Repository Directory**:
   ```bash
   cd "c:\Users\praah\OneDrive\Documents\Coding\Cars 24"
   ```

2. **Create and Activate a Virtual Environment** (Recommended):
   - On Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch Jupyter Notebook / JupyterLab** (to view notebooks):
   ```bash
   jupyter notebook
   ```

---

## ⚙️ How to Run

1. **Running the Streamlit Dashboard** (Recommended):
   - Start the interactive dashboard by running:
     ```bash
     streamlit run app.py
     ```
   - This launches a local web server (usually at `http://localhost:8501`) presenting KPI cards, interactive plots, search tables, and the live web scraper tool.

2. **Running the Scraper** (Notebook-based):
   - Open and run the cells in `Web_Scraping_Project.ipynb`.
   - *Note*: If you run this in Google Colab, it includes cells to upload/download files via `google.colab`. When running locally, you can skip the Colab-specific imports and file-download cells.

3. **Analyzing the Data** (Notebook-based):
   - Open and run the cells in `eda_on_cars24.ipynb`.
   - The notebook reads `car_data.csv` and generates multiple statistics and plots.

---

## 📈 Key Insights & Visualizations

Some of the questions answered in the EDA notebook and interactive plots:
- **Price Distribution**: Used car prices typically cluster under ₹5 Lakhs, with premium listings extending up to and beyond ₹15-20 Lakhs (which are analyzed as outliers).
- **Odometer Analysis**: A comprehensive breakdown of mileage across fuel categories, with CNG vehicles generally displaying higher odometer readings.
- **Brand Trends**: Market dominance by brands like Maruti Suzuki (e.g., Wagon R, Swift) and Hyundai (e.g., i10, Elite i20) in the used car inventory space.
- **Depreciation Trends**: Visualizations highlighting price depreciation over time by mapping listing price averages against manufacturing year.

---

## 🛠️ Dependencies

This project relies on the following libraries:
- **Streamlit** - Interactive web app dashboard framework
- **Plotly** - High-quality, interactive visualization plots
- **Pandas & NumPy** - Data manipulation and cleaning
- **Matplotlib & Seaborn** - Statistically descriptive visualizations
- **BeautifulSoup4 & Requests** - HTTP requests and HTML DOM parsing
- **SciPy** - Statistical functions
- **Jupyter Notebook** - Interactive notebook environment

