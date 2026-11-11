from django import forms

class MovieForm(forms.Form):
    rental_rate = forms.FloatField(label='Rental Rate')
    length = forms.IntegerField(label='Film Length')
    replacement_cost = forms.FloatField(label='Replacement Cost')
    RATING_CHOICES = [
        (0, 'G'),
        (1, 'PG'),
        (2, 'PG-13'),
        (3, 'R'),
    ]
    rating = forms.ChoiceField(label='Rating', choices=RATING_CHOICES)
