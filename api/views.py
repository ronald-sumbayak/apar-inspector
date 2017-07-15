import base64
import json

import requests
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import Apar, InspectionReport, PressureReport, QRCode, VerificationReport
from api.serializers import AparSerializer, InspectionReportSerializer, PressureReportSerializer, VerificationReportSerializer


class AparViewSet (generics.ListAPIView):
    queryset = Apar.objects.all ()
    serializer_class = AparSerializer


class InspectionReportList (generics.ListAPIView):
    queryset = InspectionReport.objects.all ()
    serializer_class = InspectionReportSerializer


class VerificationReportList (generics.ListAPIView):
    queryset = VerificationReport.objects.all ()
    serializer_class = VerificationReportSerializer


class PressureReportList (generics.ListAPIView):
    queryset = PressureReport.objects.all ()
    serializer_class = PressureReportSerializer


class AparRetrieve (generics.RetrieveAPIView):
    queryset = Apar.objects.all ()
    serializer_class = AparSerializer
    lookup_url_kwarg = 'id'

    
@api_view (['POST'])
def inspect (request):
    return Response (InspectionReportSerializer (
        InspectionReport.objects.create (
            apar = get_object_or_404 (Apar, id = request.data['id']),
            inspector = request.user,
            kondisi = request.data['kondisi'],
            catatan = request.data.get ('catatan')
        )
    ).data)


@api_view (['POST'])
def verify (request):
    inspection = get_object_or_404 (InspectionReport, id = request.data['id'])
    if hasattr (inspection, 'verificationreport'):
        return Response (json.loads ('{"detail": "inspection already verified"}'),
                         status = 400)
    else:
        inspection.status = request.data['status']
        inspection.save ()
        return Response (VerificationReportSerializer (
            VerificationReport.objects.create (
                inspection = inspection,
                verificator = request.user,
                status = request.data['status']
            )
        ).data)


class ReportCreate (generics.CreateAPIView):
    serializer_class = PressureReportSerializer


def media (request, filename):
    qr = QRCode.objects.get (apar__id = filename.split ('/')[-1].split ('.')[0])
    return HttpResponse (base64.b64decode (qr.base64), content_type = 'image/png')
