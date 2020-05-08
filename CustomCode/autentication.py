from rest_framework.response import Response
from rest_framework import status

def user_tokenid(something):
    def wrap(request):
        try:
            if request.META['HTTP_TOKEN_ID'] != '':
                passed = request.META['HTTP_TOKEN_ID']
                if passed != '':
                    return something(request,passed)
                else:
                    return_data = {
                    'error': "1",
                    'message': "Invalid Token"
                    }
                    return Response(return_data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return_data = {
                    "error" : "2",
                    "message" : "Token required",
                    }
                return Response(return_data, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
               return_data = {
                   "error" : "3",
                   "message" : str(e)
               }
               return Response(return_data, status=status.HTTP_401_UNAUTHORIZED)

    return wrap
