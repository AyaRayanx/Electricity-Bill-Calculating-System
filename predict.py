import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime
import time
import joblib
from db import get_db_connection
from weather_utils import get_weather_for_location

def load_data_with_weather():
    """Loads usage data and enriches it with weather data from the API."""
    conn = get_db_connection()
    # Get data and customer location
    query = """
        SELECT u.id, u.customer_id, u.year, u.month, u.consumption_kwh, c.location
        FROM usage_records u
        JOIN customers c ON u.customer_id = c.national_id
        ORDER BY u.customer_id, u.year, u.month
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return df

    # Convert month name to number if needed
    def convert_month(m):
        if isinstance(m, str) and not m.isdigit():
            try:
                return datetime.strptime(m, "%B").month
            except:
                return int(m)
        return int(m)
    
    df["month_num"] = df["month"].apply(convert_month)

    # Fetch weather for each record
    weather_data = []
    
    for index, row in df.iterrows():
        temp, precip = get_weather_for_location(row['location'], row['year'], row['month_num'])
        weather_data.append({'temp': temp, 'precip': precip})
        time.sleep(0.1)  # Be gentle with the free API

    # Add weather data to dataframe
    weather_df = pd.DataFrame(weather_data)
    df = pd.concat([df, weather_df], axis=1)

    # Create a 'previous consumption' feature (LAG)
    df['previous_consumption'] = df.groupby('customer_id')['consumption_kwh'].shift(1)
    # Drop rows where previous consumption is NaN (the first month for each customer)
    df = df.dropna(subset=['previous_consumption', 'temp', 'precip'])

    return df

def train_and_save_model():
    """Trains a model on the enriched data and saves it."""
    df = load_data_with_weather()
    if df.empty or len(df) < 10: # Check if we have enough data
        print("Not enough data to train a reliable model.")
        return None

    # Define features (X) and target (y)
    feature_columns = ['year', 'month_num', 'previous_consumption', 'temp', 'precip']
    X = df[feature_columns]
    y = df['consumption_kwh']

    if X.empty:
        print("No valid data after preparing features.")
        return None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"Model trained. MAE: {mae:.2f} kWh, R²: {r2:.2f}")

    # Save the model to a file
    joblib.dump(model, 'consumption_predictor_model.joblib')
    print("Model saved as 'consumption_predictor_model.joblib'")
    return model

def predict_for_customer(customer_id, next_year, next_month):
    """Predicts consumption for a specific customer next month."""
    try:
        model = joblib.load('consumption_predictor_model.joblib')
    except FileNotFoundError:
        print("Model not found. Please train the model first.")
        return None

    # Get the customer's last data point and location
    conn = get_db_connection()
    query = """
        SELECT u.consumption_kwh, c.location
        FROM usage_records u
        JOIN customers c ON u.customer_id = c.national_id
        WHERE u.customer_id = ?
        ORDER BY u.year DESC, u.month DESC
        LIMIT 1
    """
    last_record = pd.read_sql_query(query, conn, params=(customer_id,))
    conn.close()

    if last_record.empty:
        print(f"No historical data found for customer {customer_id}")
        return None

    last_consumption = last_record['consumption_kwh'].iloc[0]
    location = last_record['location'].iloc[0]

    # Get weather forecast for prediction month (using historical average for demo)
    forecast_temp, forecast_precip = get_weather_for_location(location, next_year, next_month)
    
    if forecast_temp is None:
        # Fallback: use average values
        forecast_temp = 20.0
        forecast_precip = 10.0

    # Create feature vector for prediction
    features = pd.DataFrame([{
        'year': next_year,
        'month_num': next_month,
        'previous_consumption': last_consumption,
        'temp': forecast_temp,
        'precip': forecast_precip
    }])

    # Predict
    prediction = model.predict(features)[0]

    # Save prediction to DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO predictions (customer_id, year, month, predicted_kwh, model)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, next_year, next_month, prediction, "RandomForest_with_Weather"))
    conn.commit()
    conn.close()

    print(f"Prediction for {customer_id}: {prediction:.2f} kWh (saved to DB)")
    return prediction

if __name__ == "__main__":
    # Train the model first
    train_and_save_model()