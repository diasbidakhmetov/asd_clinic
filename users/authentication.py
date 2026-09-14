from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class IINAuthBackend(ModelBackend):
    """Аутентификация по IIN вместо username"""
    
    def authenticate(self, request, iin=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(iin=iin)
            if user.check_password(password):
                return user
            return None
        except UserModel.DoesNotExist:
            return None
