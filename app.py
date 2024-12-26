from flask import Flask, request, render_template
import pandas as pd
import pickle

app = Flask(__name__)

# Load models and preprocessing files
with open("svm_model.pkl", "rb") as model_file:
    svm_model = pickle.load(model_file)

with open("scaler.pkl", "rb") as scaler_file:
    scaler = pickle.load(scaler_file)

with open("pca.pkl", "rb") as pca_file:
    pca = pickle.load(pca_file)

with open("feature_names.pkl", "rb") as feature_file:
    feature_names = pickle.load(feature_file)

with open("median_values.pkl", "rb") as median_file:
    median_values = pickle.load(median_file)

def detect_inhibitor(input_data):
    # Ensure input is a DataFrame with the correct feature names
    df = pd.DataFrame([input_data], columns=feature_names)

    # Drop non-numeric columns if any
    non_numeric_columns = df.select_dtypes(include=["object"]).columns
    df_cleaned = df.drop(columns=non_numeric_columns)

    # Handle missing values by filling with the median
    df_filled = df_cleaned.fillna(median_values)

    # Standardize the features
    df_scaled = scaler.transform(df_filled)

    # Apply PCA transformation
    df_pca = pca.transform(df_scaled)

    # Make prediction
    prediction = svm_model.predict(df_pca)[0]
    result = "Inhibitor" if prediction == 1 else "Non-Inhibitor"

    return result

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            input_data = pd.read_csv(file).iloc[0].to_dict()
            result = detect_inhibitor(input_data)
            return render_template("index.html", result=result)
    return render_template("index.html", result=None)

@app.route("/hello")
def hello():
    return "Hello, Flask!"

if __name__ == "__main__":
    app.run(debug=True)