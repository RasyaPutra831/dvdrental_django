from django.db import models

class CustomerAnalytics(models.Model):
    customer_id = models.IntegerField()
    total_payment = models.FloatField()
    payment_count = models.IntegerField()
    avg_payment = models.FloatField()

    def __str__(self):
        return f"Customer {self.customer_id}"

class MovieAnalytics(models.Model):
    film_id = models.IntegerField()
    rental_count = models.IntegerField()
    avg_rental_rate = models.FloatField()
    avg_length = models.FloatField()

    def __str__(self):
        return f"Film {self.film_id}"

class ModelInfo(models.Model):
    name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50)
    accuracy = models.FloatField()
    file_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.model_type})"

class PredictionHistory(models.Model):
    TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('customer', 'Customer'),
    ]

    prediction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    input_data = models.JSONField()
    prediction = models.CharField(max_length=50)
    confidence = models.FloatField()
    model_used = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prediction_type} - {self.prediction}"