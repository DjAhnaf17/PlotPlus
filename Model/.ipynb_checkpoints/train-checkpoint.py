import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
import os

# Ensure we're in the correct directory regardless from where this is run
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, '../Dataset/file.csv')
model_path = os.path.join(script_dir, 'model.pkl')

print(f"Loading data from {dataset_path}")
try:
    df = pd.read_csv(dataset_path)
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit(1)

# Prepare Features and Target
X = df.drop('Price_INR', axis=1)
y = df['Price_INR']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Model
print("Training Linear Regression model...")
model = LinearRegression()
model.fit(X_train, y_train)

# Test model internally
accuracy = model.score(X_test, y_test)
print(f"Model R^2 Score on Test Data: {accuracy:.4f}")

# Save Model
print(f"Saving model to {model_path}")
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print("Model saved successfully.")
