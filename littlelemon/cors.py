"""
Lightweight CORS middleware so that frontend pages opened via VS Code Live Server
(http://127.0.0.1:5500 or http://localhost:5500) can call the Django REST API
(http://127.0.0.1:8000/api/...) without browser CORS blocking.
"""
from django.http import HttpResponse


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)

        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken, Accept'
        return response

