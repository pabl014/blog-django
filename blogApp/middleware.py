# blogApp/middleware.py
import logging

logger = logging.getLogger('blogApp')

class SessionDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        logger.info(f"Session Data: {request.session.items()}")
        return response
