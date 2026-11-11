from django.core.management.base import BaseCommand
from django.db import connection
import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = 'ETL Movie Data for ML'

    def handle(self, *args, **kwargs):

        print("START ETL PROCESS")

        # EXTRACT
        query = """
        SELECT
            ma.film_id,
            ma.category,
            ma.total_revenue,
            ma.total_rental,
            f.length AS film_length,
            f.rating
        FROM movie_analytics ma
        JOIN film f ON ma.film_id = f.film_id;
        """

        df = pd.read_sql(query, connection)

        print("DATA LOADED:")
        print(df.head())


        # TRANSFORM

        # 1. Encode rating
        rating_map = {
            'G': 0,
            'PG': 1,
            'PG-13': 2,
            'R': 3,
            'NC-17': 4
        }
        df['rating'] = df['rating'].map(rating_map)

        #  2. Encode category
        df['category'] = df['category'].astype('category').cat.codes

        #  3. CREATE TARGET (pakai total_rental)
        threshold = df['total_rental'].quantile(0.7)
        df['is_popular'] = (df['total_rental'] > threshold).astype(int)

        #  4. CREATE predict_month (SIMULASI)
        df['predict_month'] = np.random.randint(1, 7, size=len(df))

        print("\nTHRESHOLD:", threshold)
        print("\nDATA AFTER TRANSFORM:")
        print(df.head())

        # FINAL DATASET
        df_final = df[[
            'category',
            'total_revenue',
            'film_length',
            'rating',
            'predict_month',
            'is_popular'
        ]]

        # SAVE CSV
        df_final.to_csv('movie_ml_dataset.csv', index=False)

        print("\nETL DONE!")
        print("File saved: movie_ml_dataset.csv")
        print("\nETL COMPLETE")