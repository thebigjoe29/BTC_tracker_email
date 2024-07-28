# pricing/views.py
import json

from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from pricing.bg_task import check_price_and_send_email
from pricing.models import CustomUser

from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import authenticate
from django.http import JsonResponse

from rest_framework_simplejwt.tokens import RefreshToken

from pricing.serializer import AlertSerializer
from .models import Alert, CustomUser
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def price_alert(request):
        
        price = request.data['price']
        email = request.user.email
        alert = Alert.objects.create(email=email, price=price)

        check_price_and_send_email.apply_async((alert.id,))
        
        alert.save()

        return Response({'message': 'Alert created and monitoring started.'}, status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_alert(request,alert_id):
    try:     
        
        alert = Alert.objects.get(id=alert_id)
        alert.status = 'deleted'
        alert.save()
        return Response({'message': 'Alert status updated to deleted.'}, status=status.HTTP_200_OK)
    except Alert.DoesNotExist:
        return Response({'error': 'Alert not found or not authorized.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_alerts(request,status):
    
    cache_key = f'alerts_{status}_page_{request.GET.get("page", 1)}'
    
    
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)
    alerts=Alert.objects.filter(status=status)
    paginator = PageNumberPagination()
    paginator.page_size = 10  
    result_page = paginator.paginate_queryset(alerts, request)
    serializer = AlertSerializer(result_page, many=True)
    response_data = paginator.get_paginated_response(serializer.data)
    cache.set(cache_key, response_data.data, timeout=60*15) 
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_alerts(request):    
    cache_key = f'all_alerts_page_{request.GET.get("page", 1)}'
    
   
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)
    alerts=Alert.objects.all()
    paginator = PageNumberPagination()
    paginator.page_size = 10  
    result_page = paginator.paginate_queryset(alerts, request)
    serializer = AlertSerializer(result_page, many=True)
    response_data = paginator.get_paginated_response(serializer.data)
    cache.set(cache_key, response_data.data, timeout=60*15) 
    return paginator.get_paginated_response(serializer.data)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            password = data['password']
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already registered'}, status=400)
            
            user = CustomUser.objects.create_user(
                email=email,
                password=password
            )
            return JsonResponse({'email': user.email}, status=201)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            password = data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                refresh["email"] = email
                
                return JsonResponse({
                    
                    'JWT token': str(refresh.access_token),
                }, status=200)
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)
