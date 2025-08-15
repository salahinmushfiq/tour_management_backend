# middleware.py

class LogAuthHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.headers.get('Authorization', None)
        print(f"Authorization header: {auth}")
        print(f"request.META HTTP_AUTHORIZATION: {request.META.get('HTTP_AUTHORIZATION')}")
        response = self.get_response(request)
        return response

class PrintMetaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        print("META Authorization header:", request.META.get("HTTP_AUTHORIZATION"))
        return self.get_response(request)