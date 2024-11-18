# middlewares.py

from django.http import JsonResponse

class GreetingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/welcome':
            greeting = self.get_greeting()
            return JsonResponse({'greeting': greeting})
        response = self.get_response(request)
        return response

    def get_greeting(self):
        # Aquí puedes obtener el saludo desde una configuración o base de datos
        return 'Hello, welcome to our site!'
