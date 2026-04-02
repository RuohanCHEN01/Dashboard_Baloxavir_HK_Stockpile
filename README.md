# Baloxavir Stockpile Dashboard

## Project Description
The Baloxavir Stockpile Dashboard is a web-based interface designed to monitor and analyze the stockpile of Baloxavir, an antiviral medication. The dashboard provides real-time insights into the availability and distribution of the drug across various locations, enabling health authorities and stakeholders to make informed decisions.

## Setup Instructions
1. **Clone the Repository**  
   To get started, clone the repository to your local machine:
   ```bash
   git clone https://github.com/RuohanCHEN01/Dashboard_Baloxavir_HK_Stockpile.git
   cd Dashboard_Baloxavir_HK_Stockpile
   ```  
2. **Install Dependencies**  
   Ensure you have Node.js installed, then install the required packages:
   ```bash
   npm install
   ```  
3. **Configuration**  
   Update the configuration files with your local settings, including database connections and API keys.

4. **Run the Application**  
   Start the application:
   ```bash
   npm start
   ```

## Usage Guide
- Navigate to `http://localhost:3000` in your web browser to access the dashboard.
- Use the navigation menu to explore various sections, including stockpile status, distribution analytics, and historical data views.

## Features Overview
- **Real-Time Monitoring**  
   Keep track of current stock levels across different locations.
- **Interactive Analytics**  
   Visualize data trends and patterns with dynamic charts and graphs.
- **User Authentication**  
   Secure access to the dashboard with user login capabilities.
- **Data Export**  
   Export data reports in multiple formats (CSV, PDF).

## Data Pipeline Explanation
The data pipeline consists of several key components that facilitate data ingestion, processing, and visualization:
1. **Data Ingestion**  
   Data is collected from various sources, including internal databases and APIs.
2. **Data Processing**  
   The collected data is cleaned, transformed, and stored in a relational database for easy retrieval.
3. **Data Visualization**  
   The dashboard utilizes frontend libraries to render visual representations of the processed data, enabling users to gain insights efficiently.

## Troubleshooting
- **Common Issues**  
   - If you encounter issues with dependencies, ensure all Node packages are correctly installed. Delete the `node_modules` folder and run `npm install` again if necessary.
   - If the application doesn't start, check for any error messages in the console and verify your configuration settings.
- **Support**  
   For further assistance, please open an issue in the GitHub repository or contact the project maintainers directly.