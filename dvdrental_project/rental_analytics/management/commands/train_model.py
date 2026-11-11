from django.core.management.base import BaseCommand
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
from rental_analytics.models import ModelInfo


class Command(BaseCommand):
    help = 'Train ML model (WITH PREDICT_MONTH)'

    def handle(self, *args, **kwargs):

        print("\nTRAINING MOVIE MODEL\n")

        # LOAD DATA
        df = pd.read_csv('movie_ml_dataset.csv')

        print("DATA LOADED:")
        print(df.head())

        # FEATURE & TARGET
        X = df[['category', 'total_revenue', 'film_length', 'rating', 'predict_month']]
        y = df['is_popular']

        # SPLIT DATA
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # MODEL
        model = RandomForestClassifier(
            n_estimators=120,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )

        print("\nTraining model...")
        model.fit(X_train, y_train)

        # EVALUATION
        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)

        print("\nRESULT")
        print(f"Train Accuracy : {train_acc * 100:.2f}%")
        print(f"Test Accuracy  : {test_acc * 100:.2f}%")
        print("\n")

        # FEATURE IMPORTANCE
        importance = model.feature_importances_
        feature_names = X.columns

        print("FEATURE IMPORTANCE:")
        for name, score in zip(feature_names, importance):
            print(f"{name}: {score:.4f}")

        # SAVE MODEL
        joblib.dump(model, 'movie_rf.pkl')

        ModelInfo.objects.create(
            name="Movie RF + Predict Month",
            model_type="MOVIE_RF",
            accuracy=test_acc,
            file_path="movie_rf.pkl"
        )

        print("\nModel saved: movie_rf.pkl")
        print("\nDONE\n")