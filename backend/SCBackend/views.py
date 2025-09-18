#api 
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
@require_http_methods(['POST'])
def test_angular(request):
    data = json.loads(request.body)
    user = data.get('username')
    password = data.get('password')
    
    if user =='HOLAMUNDO' and password == '123':
        return JsonResponse({'success': True, 'username':'HOLAMUNDO', 'password': '123'})
    else:
        return JsonResponse({'success': False, 'error_messages' : 'CODE_L1'})    