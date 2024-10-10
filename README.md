# 🌍 Istanbul Earthquake Awareness and Risk Assessment Platform

This project aims to provide a comprehensive platform for raising awareness and preparing the residents of Istanbul for potential earthquake scenarios, specifically focusing on the 7.5 Mw earthquake expected in the region. By utilizing advanced data analysis, AI-based predictions, and interactive visualizations, the platform seeks to inform users about risk factors and potential consequences while offering personalized recommendations for earthquake preparedness. The dataset used in this project was provided by the Istanbul Metropolitan Municipality and was last updated on March 2, 2023.

<img src="Earthquake Risk/static/images/model.jpeg" alt="home" width="850" height="450">  <!-- Add an image relevant to your project -->

---

## 🏠 Project Overview

The Istanbul Earthquake Awareness and Risk Assessment Platform is designed to give users insights into earthquake risks at both a regional and district level. It combines real-time earthquake data, risk mapping, AI-based risk predictions, and detailed data visualizations to create an educational tool for the public. This platform is developed using Flask for backend services, Bootstrap for front-end design, and various data visualization libraries to offer a rich and engaging user experience.

The platform is divided into several core features:

1. **Home Page**: Provides an introduction to the project and a brief overview of its objectives.
2. **Recent Earthquakes**: Displays real-time earthquake data for Turkey, including a heatmap and detailed markers.
3. **Risk Map**: An interactive map categorizing Istanbul districts into risk levels based on potential damage and casualties.
4. **Data Analysis**: Visualizes key statistics related to potential earthquake impacts across districts.
5. **AI-Based Predictions**: Offers personalized risk assessments based on user-selected districts and neighborhoods.
6. **Preparedness Information**: Provides essential tips and guidelines on what to do before, during, and after an earthquake.

---

## 🌐 Features

### 1. **Home Page**
The homepage of the platform offers a clean and modern interface, introducing users to the core mission of the project. The goal is to raise awareness and educate the residents of Istanbul about the risks associated with earthquakes. The homepage outlines the project’s key features and encourages users to explore further.

### 2. **Recent Earthquakes**
This section provides users with an up-to-date list of earthquakes that have occurred within the last 24 hours across Turkey. The data is presented through:
- **Interactive Maps**: Using the Folium library, users can explore a map with markers representing earthquake locations. Clicking on a marker reveals detailed information such as magnitude, depth, and the exact location of the earthquake.
- **Heatmaps**: A visual representation of earthquake density across Turkey, highlighting the most earthquake-prone areas.

The earthquake data is fetched in real-time through web scraping from the Kandilli Observatory, ensuring that users have the latest information.

### 3. **Risk Map**
The Risk Map provides a detailed overview of Istanbul's earthquake risk, broken down by district. This map is interactive and color-coded to represent different levels of risk:
- **High-Risk Areas**: Districts expected to experience severe damage, loss of life, and injuries in the event of an earthquake.
- **Significant Risk Areas**: Districts where moderate to significant damage is expected.
- **Monitoring Required Areas**: Districts with lower risks but still in need of regular monitoring for potential hazards.
- **Low-Risk Areas**: Districts where minimal damage and casualties are expected.

The map uses Folium for interactive navigation, allowing users to zoom in on specific districts and neighborhoods for more localized information.

### 4. **Data Analysis**
This section presents detailed data visualizations to help users understand the potential impact of an earthquake in Istanbul. The dataset includes variables such as:
- **Severely Damaged Buildings**: Number of buildings expected to collapse.
- **Moderately Damaged Buildings**: Buildings that will sustain significant but not complete structural damage.
- **Slightly Damaged Buildings**: Buildings that will sustain minor damages.
- **Loss of Life**: Projected fatalities in each district.
- **Severe Injuries**: The number of people expected to suffer serious injuries.
- **Infrastructure Damage**: Damage to water, gas, and sewage pipes.
- **Sheltering Needs**: The estimated number of people who will need temporary shelter following an earthquake.

Visualizations are created using Plotly to allow users to interact with the data, making it easier to understand the potential damage and the areas most at risk.

### 5. **AI-Based Predictions**
One of the most powerful features of the platform is its AI-based risk prediction tool. Using machine learning models, the platform predicts the likelihood of various risk factors in different districts. Users can select their district and neighborhood to receive predictions on:
- **Building Risk**: The likelihood of building collapse or severe structural damage.
- **Casualty Risk**: The probability of fatalities and severe injuries.
- **Personnel Requirement Risk**: The anticipated need for emergency personnel.
- **Fire Risk**: The chances of fires breaking out following the earthquake.
- **Disease Risk**: The likelihood of disease outbreaks due to disrupted services and conditions post-earthquake.
- **Shelter Risk**: The need for emergency shelters and the capacity required to accommodate displaced individuals.

These predictions provide a personalized earthquake risk profile for users, helping them understand the specific threats they may face and prepare accordingly.

### 6. **Preparedness Information**
Preparedness is key to surviving and mitigating the effects of an earthquake. This section of the platform provides users with critical information on how to prepare for an earthquake, including:
- **Before the Earthquake**: Tips on creating an emergency kit, securing heavy objects, and planning escape routes.
- **During the Earthquake**: Advice on what to do when the shaking starts, including the "Drop, Cover, Hold On" technique.
- **After the Earthquake**: Guidelines on how to check for injuries, avoid hazardous areas, and locate assembly points for safety.

This section also includes a list of official **Assembly Points** provided by AFAD, helping users find the nearest safe locations to gather after an earthquake.

---

## 🎯 Usage Guide
Once the application is running, you can navigate through the following sections:

- **Home Page**: Introduction and overview of the project.
- **Recent Earthquakes**: View interactive maps showing recent seismic activity.
- **Risk Map**: Explore Istanbul’s risk areas categorized by different risk levels.
- **Data Analysis**: Deep dive into earthquake statistics and visualizations.
- **AI Predictions**: Input your location for personalized earthquake risk predictions.
- **Preparedness**: Learn about earthquake safety measures and assembly points.

---

## 🛠️ Technologies Used

- **Flask**: The web framework used for building the backend of the platform.
- **Bootstrap 5**: For creating a responsive and modern front-end design.
- **Folium**: A Python library for creating interactive maps, used for visualizing earthquake locations and risk maps.
- **Plotly**: Libraries for creating detailed and interactive data visualizations.
- **BeautifulSoup**: Used for web scraping real-time earthquake data from the Kandilli Observatory.
- **Pandas & NumPy**: For data processing and manipulation.
- **Scikit-learn**: Used for building the machine learning models that power the AI-based risk predictions.

---

##💡 Future Enhancements
📈 Real-Time Data Integration: Incorporate live data feeds from global earthquake monitoring agencies.
🤖 Advanced Machine Learning Models: Use more sophisticated AI models for more accurate risk assessments.

---

## ⚙️ Installation

To set up the project on your local machine, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/username/Istanbul-earthquake-Scenario.git
cd Istanbul-Earthquake-Scenario
