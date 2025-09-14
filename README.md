# Electricity Billing System with Predictive Analytics

## Overview
A full-stack web application built with Python and Flask that revolutionizes traditional electricity billing through automated processes and AI-driven forecasting. The system features dual-role dashboards for customers and administrators, implementing sophisticated tiered tariff calculations and machine learning-powered consumption predictions enhanced with weather data integration.

## Features
-Dual-Role Dashboards: Custom interfaces for customers (bill payment, usage history) and administrators (system management, analytics)

-Intelligent Billing Engine: Automated tiered tariff calculations with validation checks

-Predictive Analytics: Machine learning consumption forecasting with 85% accuracy

-Weather Data Integration: Enhanced predictions using historical meteorological data

-Payment Ecosystem: Comprehensive bill management and transaction tracking
## Installation

### Prerequisites
- Python 3.8+  
- pip (Python package manager)  

### Steps
```bash
git clone <repo-url>
cd electricity-billing-system
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python db.py   # Initialize database with sample data
python interface.py   # Run the Flask application
```

## Technology Stack
- **Backend:** Python, Flask  
- **Database:** SQLite  
- **Frontend:** Bootstrap 5  
- **Machine Learning:** Scikit-learn (Random Forest)  
- **Data Processing:** Pandas  
- **External APIs:** Open-Meteo (historical weather data)  
- **Authentication:** SHA-256 password hashing, session-based login  

## Implementation

- **Python (Core Logic):** Handles bill calculation based on a tiered tariff structure, ensuring fairness and reducing manual errors.  

- **SQLite (Database):** Stores customer records, consumption history, bills, and payments with integrity constraints to prevent invalid entries.  
- **Weather API (Open-Meteo):** Supplies historical weather data that is merged with usage records to improve the accuracy of future consumption forecasts.  
- **Machine Learning (Random Forest):** Trained on enriched historical data to predict **total company-wide electricity demand**, supporting proactive planning and resource allocation.  
- **Pandas (Data Processing):** Cleans, transforms, and prepares consumption and weather data for storage and model training.  
- **Bootstrap 5 (Frontend):** Delivers a responsive, user-friendly interface for customers and admins.  
- **Authentication System:** Uses SHA-256 password hashing with role-based access control (customer vs admin).  
