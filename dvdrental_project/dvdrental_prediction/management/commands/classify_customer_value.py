import pandas as pd
import joblib
from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from dvdrental_prediction.models import ModelInfo

class Command(BaseCommand):
    help = "Train model to classify customer value and save it"

    def handle(self, *args, **kwargs):
        # 1. load csv
        df = pd.read_csv('customer_payment_data.csv')

        # 2. create target label
        df['value_label'] = (df['total_payment'] > 100).astype(int)

        # 3. define features and label
        features = ['store_id', 'active', 'total_payment', 'payment_count', 'average_payment']
        x = df[features]
        y = df['value_label']

        # 4. train/test split
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        # 5. train model
        model = RandomForestClassifier()
        model.fit(x_train, y_train)

        # 6. evaluate
        predictions = model.predict(x_test)
        report = classification_report(y_test, predictions)
        self.stdout.write(self.style.SUCCESS('Classification Report:\n' + report))

        # 7. save model (SAMAKAN NAMA DENGAN VIEWS 🔥)
        model_filename = 'final_customer_model.pkl'
        joblib.dump(model, model_filename)
        self.stdout.write(self.style.SUCCESS(f'Model saved to {model_filename}'))

        # 8. save model info ke DB (FIX DI SINI)
        model_info = ModelInfo.objects.create(
            model_name='RandomForestClassifier',
            training_data='customer_payment_data.csv',
            model_summary=report
        )

        self.stdout.write(self.style.SUCCESS(f'Model info saved to db: ID {model_info.id}'))