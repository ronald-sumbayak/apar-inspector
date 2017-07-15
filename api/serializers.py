from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import PressureReport, VerificationReport, Apar, InspectionReport


class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = '__all__'


class AparSerializer (serializers.ModelSerializer):
    inspector = serializers.ReadOnlyField (source = 'inspector.username')
    
    class Meta:
        model  = Apar
        fields = '__all__'


class InspectionReportSerializer (serializers.ModelSerializer):
    apar = serializers.ReadOnlyField (source = 'apar.identifier')
    inspector = serializers.ReadOnlyField (source = 'inspector.username')
    
    class Meta:
        model  = InspectionReport
        fields = '__all__'


class VerificationReportSerializer (serializers.ModelSerializer):
    class Meta:
        model  = VerificationReport
        fields = '__all__'


class PressureReportSerializer (serializers.ModelSerializer):
    class Meta:
        model  = PressureReport
        fields = '__all__'