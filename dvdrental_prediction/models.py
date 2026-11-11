from django.db import models

class Movie(models.Model):
    film_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    release_year = models.IntegerField()
    rating = models.CharField(max_length=5)
    language = models.ForeignKey('Language', on_delete=models.DO_NOTHING, db_column='language_id')
    actors = models.ManyToManyField('Actor', through='FilmActor')

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'film'
        managed = False

class Language(models.Model):
    language_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'language'
        managed = False
    
    def __str__(self):
        return self.name
    
class Actor(models.Model):
    actor_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)

    class Meta:
        db_table = 'actor'
        managed = False

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class FilmActor(models.Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, db_column='actor_id')
    film = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='film_id')

    class Meta:
        db_table = 'film_actor'
        unique_together = ('film', 'actor')
        managed = False

class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=25)

    class Meta:
        db_table = 'category'
        managed = False

    def __str__(self):
        return self.name
    
class FilmCategory(models.Model):
    film = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='film_id')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')

    class Meta:
        db_table = 'film_category'
        unique_together = ('film', 'category')
        managed = False

class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    store_id = models.IntegerField()
    address_id = models.IntegerField()
    active = models.BooleanField()
    create_date = models.DateTimeField()

    class Meta:
        db_table = 'customer'
        managed = False

class Payment(models.Model):
    payment_id = models.IntegerField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, db_column='customer_id')
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    payment_date = models.DateTimeField()

    class Meta:
        db_table = 'payment'
        managed = False

class ModelInfo(models.Model):
    model_name = models.CharField(max_length=100)
    training_date = models.DateTimeField(auto_now_add=True)
    training_data = models.TextField()
    model_summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.model_name