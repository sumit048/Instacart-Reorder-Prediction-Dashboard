# pipeline/training.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import logging
import os

def train_model(df, model_path="artifacts/model.joblib"):
    """
    Train a plain RandomForestClassifier to predict 'reordered'.
    """
    try:
        logging.info("Preparing training data...")

        # Drop missing values
        df = df.dropna()

        # Encode product_name (if exists)
        if "product_name" in df.columns:
            le = LabelEncoder()
            df["product_name_encoded"] = le.fit_transform(df["product_name"])
            df.drop(columns=["product_name"], inplace=True)

        # Check target
        if "reordered" not in df.columns:
            raise ValueError("'reordered' column not found in data.")

        # Split features and labels
        X = df.drop("reordered", axis=1)
        y = df["reordered"]

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train simple RandomForest model
        clf = RandomForestClassifier(
            n_estimators=10,
            max_depth=10,
            max_features="sqrt",
            random_state=42
        )
        clf.fit(X_train, y_train)

        # Evaluate
        y_pred = clf.predict(X_test)
        print("📊 Classification Report:\n", classification_report(y_test, y_pred))
        print("✅ Accuracy:", round(accuracy_score(y_test, y_pred) * 100, 2), "%")

        # Save confusion matrix plot
        cm = confusion_matrix(y_test, y_pred)
        os.makedirs("artifacts", exist_ok=True)
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=["Not Reordered", "Reordered"],
                    yticklabels=["Not Reordered", "Reordered"])
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.title("Confusion Matrix")
        plt.tight_layout()
        plt.savefig("artifacts/confusion_matrix.png")
        plt.close()

        # Save model
        joblib.dump(clf, model_path)
        logging.info(f"✅ Model saved to: {model_path}")

    except Exception as e:
        logging.error(f"❌ Training failed: {e}")
        print(f"❌ Training failed: {e}")

# Entry point
if __name__ == "__main__":
    # Load dataset (adjust path if needed)
    df = pd.read_csv("artifacts/cleaned_data.csv", nrows=10000)
    train_model(df)
