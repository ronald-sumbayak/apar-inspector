from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import PressureReport, VerificationReport, Apar, InspectionReport, UserAccessLevel


class UserAccessLevelSerializer (serializers.ModelSerializer):
    class Meta:
        model  = UserAccessLevel
        fields = '__all__'


class AparSerializer (serializers.ModelSerializer):
    inspector = serializers.ReadOnlyField (source = 'inspector.username')
    
    class Meta:
        model  = Apar
        fields = '__all__'


class InspectionReportSerializer (serializers.ModelSerializer):
    apar = serializers.ReadOnlyField (source = 'apar.identifier')
    aparid = serializers.ReadOnlyField (source = 'apar.id')
    inspector = serializers.ReadOnlyField (source = 'inspector.username')
    verification = serializers.ReadOnlyField (source = 'verificationreport.id')
    
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