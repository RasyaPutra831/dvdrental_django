from django.core.management.base import BaseCommand
import pandas as pd
from django.db.models import Sum
from dvdrental_prediction.models import Customer, Payment

class Command(BaseCommand):
    help = "ETL: Extract customer and payment data and save as csv"

    def handle(self, *args, **kwargs):
        data = []

        for customer in Customer.objects.all():
            payments = Payment.objects.filter(customer=customer)
            total_payment = payments.aggregate(total=Sum('amount'))['total'] or 0
            payment_count = payments.count()
            average_payment = total_payment / payment_count if payment_count > 0 else 0
            data.append({
                'customer_id': customer.customer_id,
                'store_id': customer.store_id,
                'active' : customer.active,
                'create_date': customer.create_date,
                'total_payment': total_payment,
                'payment_count': payment_count,
                'average_payment': average_payment,
            })

        df = pd.DataFrame(data)
        df.to_csv('customer_payment_data.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Customer payment dataset saved to csv'))