# DVD Rental Analytics (Django)

Course project built on the PostgreSQL `dvdrental` sample database.

- ETL: `python manage.py etl_customer_payment` extracts customer and payment data, aggregates it with pandas, and saves `customer_payment_data.csv`
- Model: `python manage.py classify_customer_value` trains a RandomForest classifier on the ETL output
- Web app: movie search, autocomplete, and movie popularity prediction

## Setup

```
pip install -r requirements.txt
set DB_PASSWORD=your_postgres_password   (Windows)
python manage.py runserver
```

Database settings are read from the environment variables DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.

## CI

GitHub Actions runs a lint, `manage.py check`, and the test suite on every push and pull request.
