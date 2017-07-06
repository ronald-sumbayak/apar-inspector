from django.contrib.auth.models import User
from rest_framework import serializers

from dashboard.models import Apar

class AparSerializer (serializers.ModelSerializer):
    inspector = serializers.ReadOnlyField (source = 'inspector.username')
    
    class Meta:
        model  = Apar
        fields = '__all__'


class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = '__all__'
