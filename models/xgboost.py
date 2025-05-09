# -*- coding: utf-8 -*-
"""XGBoost.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ciuLOVDmOdlBcqQJgFrPpcQzEcDd6mFg
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
from xgboost import plot_importance
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error, r2_score

# Load the CSV file
data = pd.read_csv('player_stats.csv')

# Step 1: Clean data
# Convert height and weight to numeric
data['height'] = data['height'].astype(str)
data['weight'] = data['weight'].astype(str)
data['wage'] = data['wage'].astype(str)

data['height'] = data['height'].str.split().str[0]
data['weight'] = data['weight'].str.split().str[0]
data['wage'] = data['wage'].str.replace('$', '').str.strip()

# Convert to float
data['height'] = data['height'].astype(float)
data['weight'] = data['weight'].astype(float)
data['wage'] = data['wage'].astype(float)

data.head()

data = data.dropna(subset=['wage'])
data.head()

data = data.drop('defence_avg',axis=1)
data = data.drop('value',axis=1)
data = data.drop('Marking',axis=1)
#df.drop('B', axis=1, inplace=True)

#categorical
categorical_columns = ['pref_foot', 'birthdate', 'pref_pos', 'work_rate', 'joined_club', 'contract_expires']
label_encoder = LabelEncoder()

for column in categorical_columns:
    data[column] = label_encoder.fit_transform(data[column].astype(str))

data.head()

X = data.drop(['name', 'wage'], axis=1)
y = data['wage']

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = xgb.XGBRegressor(random_state=42)
model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = model.predict(X_test_scaled)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

mse, r2

# Visualize feature importance
plt.figure(figsize=(10, 8))
plot_importance(model, max_num_features=20)
plt.title("Top 20 Important Features")
plt.show()

plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred, alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel("Actual Wage")
plt.ylabel("Predicted Wage")
plt.title("Actual vs Predicted Wage")
plt.show()

