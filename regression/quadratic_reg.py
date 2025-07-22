import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

# Read data
df = pd.read_csv('dataset.csv', header=None, names=["x1", "x2", "y1", "y2"])
X = df[["x1", "x2"]].values
y = df[["y1", "y2"]].values

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create polynomial features (degree=2 for quadratic, degree=3 for cubic, etc.)
degree = 2
poly_features = PolynomialFeatures(degree=degree, include_bias=True)

# Create pipeline with polynomial features and linear regression
model = Pipeline([
    ('poly', poly_features),
    ('linear', LinearRegression())
])

# Train model
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Get the feature names and coefficients for interpretation
feature_names = poly_features.get_feature_names_out(['x1', 'x2'])
linear_model = model.named_steps['linear']

print("Nonlinear regression equations:")
print(f"Features: {feature_names}")
print("\nCoefficients for y1:")
for i, (feature, coef) in enumerate(zip(feature_names, linear_model.coef_[0])):
    print(f"  {feature}: {coef:.4f}")
print(f"Intercept for y1: {linear_model.intercept_[0]:.4f}")

print("\nCoefficients for y2:")
for i, (feature, coef) in enumerate(zip(feature_names, linear_model.coef_[1])):
    print(f"  {feature}: {coef:.4f}")
print(f"Intercept for y2: {linear_model.intercept_[1]:.4f}")

# Construct readable equations
def format_equation(coeffs, intercept, target_name):
    terms = []
    for feature, coef in zip(feature_names, coeffs):
        if abs(coef) > 1e-10:  # Skip very small coefficients
            if feature == '1':  # Skip the bias term (it's handled by intercept)
                continue
            sign = '+' if coef >= 0 else '-'
            terms.append(f"{sign} {abs(coef):.4f}*{feature}")
    
    equation = f"{target_name} = {intercept:.4f}"
    for term in terms:
        equation += f" {term}"
    return equation

print("\nReadable equations:")
print(format_equation(linear_model.coef_[0], linear_model.intercept_[0], "y1"))
print(format_equation(linear_model.coef_[1], linear_model.intercept_[1], "y2"))

# Evaluate
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)
print(f"\nMSE: {mse:.4f}, R²: {r2:.4f}")

# Optional: Try different degrees and compare
print("\nComparison of different polynomial degrees:")
for deg in [1, 2, 3, 4]:
    poly_model = Pipeline([
        ('poly', PolynomialFeatures(degree=deg, include_bias=True)),
        ('linear', LinearRegression())
    ])
    poly_model.fit(X_train, y_train)
    pred = poly_model.predict(X_test)
    mse_deg = mean_squared_error(y_test, pred)
    r2_deg = r2_score(y_test, pred)
    print(f"Degree {deg}: MSE={mse_deg:.4f}, R²={r2_deg:.4f}")