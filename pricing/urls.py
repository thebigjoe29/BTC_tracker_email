
from django.urls import path
from .views import delete_alert, list_alerts, list_all_alerts, price_alert
from .views import register, login
urlpatterns = [
    path('alerts/create/', price_alert, name='create-alert'),
    path('alerts/delete/<int:alert_id>/', delete_alert, name='delete-alert'),
    path('alerts/<str:status>/', list_alerts, name='list-alerts'),
    path('alerts/', list_all_alerts, name='list-all-alerts'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
]
