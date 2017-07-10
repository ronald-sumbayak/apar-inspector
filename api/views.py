import base64
import io
import os
import qrcode
import sys
from datetime import date
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from aparinspector import settings
from api.serializers import AparSerializer, UserSerializer
from dashboard.models import Apar, QRCode

@api_view (['POST'])
def add (request):
    serializer = AparSerializer (data = request.data)
    if serializer.is_valid ():
        serializer.save ()
        return Response (serializer.data, status = 200)
    return Response (serializer.errors, status = 400)

class AparDetail (APIView):
    def get (self, request, id):
        apar = get_object_or_404 (Apar, id = id)
        return Response (AparSerializer (apar).data)
    
    def put (self, request, id):
        apar = get_object_or_404 (Apar, id = id)
        serializer = AparSerializer (apar, request.data)
        if serializer.is_valid ():
            serializer.save ()
            return Response (serializer.data)
        return Response (serializer.errors, status = 400)
    
    def delete (self, request, id):
        apar = get_object_or_404 (Apar, id = id)
        apar.delete ()
        return Response ()

    
@api_view (['POST'])
def inspect (request, id):
    instance = get_object_or_404 (Apar, id = id)
    if request.data.get ('catatan'):
        instance.catatan = request.data['catatan']
    instance.kondisi = request.data['kondisi']
    instance.inspector = request.user
    instance.pengecekan = date.today ()
    instance.save ()
    return Response (AparSerializer (instance).data)

@api_view (['POST'])
def refill (request, id):
    instance = get_object_or_404 (Apar, id = id)
    instance.pengisian = date.today ()
    instance.inspector = request.user
    instance.save ()
    return Response (AparSerializer (instance).data)


class AparViewSet (generics.ListAPIView):
    queryset         = Apar.objects.all ()
    serializer_class = AparSerializer


class UserViewSet (generics.ListAPIView):
    queryset         = User.objects.all ()
    serializer_class = UserSerializer


def media (request, filename):
    filename = filename.split ('/')[-1]
    filename = filename.split ('.')[0]
    qr = QRCode.objects.get (apar__id = filename)
    # return HttpResponse ("data:image/jpg;base64,%s" % base64.b64decode (qr.base64), content_type = 'image/png')
    return HttpResponse (base64.b64decode (qr.base64), content_type = 'image/png')