
from celery import Celery
from .models import Alert
from django.core.mail import send_mail
import time
import requests

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')
@app.task
def check_price_and_send_email(alert_id):
    try:
        alert = Alert.objects.get(id=alert_id)
        while alert.status == 'created':
            current_price = get_bitcoin_price()
            if current_price >= alert.price:
                send_mail(
                    'Price Alert',
                    f'The current Bitcoin price is {current_price}, which is greater than or equal to your threshold of {alert.price}.',
                    'thebigjoe29@gmail.com',
                    [alert.email],
                    fail_silently=False,
                )
                alert.status = 'triggered'
                alert.save()
                return 'Email sent.'
            time.sleep(10)  
    except Alert.DoesNotExist:
        return 'Alert does not exist.'

def get_bitcoin_price():
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
        response.raise_for_status()
        data = response.json()
        return float(data['price'])
    except requests.RequestException as e:
        print(f"Error fetching Bitcoin price: {e}")
        return None
