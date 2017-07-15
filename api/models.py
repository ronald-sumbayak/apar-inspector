import base64
import io
import json
import os

import qrcode
import sys

import requests
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse
from rest_framework.authtoken.models import Token

from aparinspector import settings

class Apar (models.Model):
    lokasi            = models.CharField (max_length = 128)
    nomor_lokasi      = models.CharField (max_length = 8)
    jenis             = models.CharField (max_length = 8)
    kapasitas         = models.IntegerField ()
    kadaluarsa        = models.DateField ()
    inspeksi_terakhir = models.ForeignKey ('VerificationReport', blank = True, null = True)
    
    @property
    def identifier (self):
        return '%s (%s)' % (self.lokasi, self.nomor_lokasi)
    
    def __str__ (self):
        return self.identifier


class InspectionReport (models.Model):
    apar           = models.ForeignKey (Apar)
    inspector      = models.ForeignKey (User)
    kondisi        = models.IntegerField (choices = (
        (1, 'Baik'),
        (0, 'Tidak Baik')
    ))
    catatan        = models.TextField (max_length = 1024, blank = True, null = True)
    waktu_inspeksi = models.DateTimeField (auto_now_add = True)
    
    def __str__ (self):
        return '%s | %s' % (self.apar.__str__ (), self.inspector.__str__ ())


class VerificationReport (models.Model):
    inspection       = models.OneToOneField (InspectionReport)
    verificator      = models.ForeignKey (User)
    status           = models.IntegerField (choices = (
        (0, 'Ditolak'),
        (1, 'Terverifikasi')
    ))
    waktu_verifikasi = models.DateTimeField (auto_now_add = True)
    
    def __str__ (self):
        return '%s | %s' % (self.inspection.__str__ (),
                            self.verificator)


class PressureReport (models.Model):
    pembuka = models.CharField (max_length = 64)
    penutup = models.CharField (max_length = 64)
    t = models.IntegerField ()
    p = models.IntegerField ()
    b = models.IntegerField ()
    nomor = models.CharField (max_length = 16)
    waktu = models.DateTimeField (auto_now_add = True)
    
    def __str__ (self):
        return '%s | %s | %s' % (self.t, self.p, self.b)
    
    @property
    def body (self):
        return "%s %s %s %s %s" % (self.pembuka, self.t, self.p, self.b, self.penutup)


class QRCode (models.Model):
    apar   = models.OneToOneField (Apar)
    image  = models.ImageField (upload_to = 'qrcode')
    base64 = models.CharField (max_length = 1024)
    
    def __str__ (self):
        return self.apar.__str__ ()


@receiver (post_save, sender = User)
def create_auth_token (sender, instance = None, created = False, **kwargs):
    if created:
        Token.objects.create (user = instance)


@receiver (post_save, sender = VerificationReport)
def apply_inspection (sender, instance = None, created = False, **kwargs):
    if created:
        apar = instance.inspection.apar
        apar.inspeksi_terakhir = instance
        apar.save ()


@receiver (post_save, sender = Apar)
def generate_qrcode (sender, instance = None, created = False, **kwargs):
    if created:
        stream = io.BytesIO ()
        qrcode.make (instance.id).save (stream)
        
        name = '%s.png' % (instance.id)
        content_type = 'image/png'
        qr = QRCode.objects.create (apar = instance)
        qr.image.save (name, InMemoryUploadedFile (
            stream, None, name, content_type,
            sys.getsizeof (stream), None))
        
        file = os.path.join (os.path.join (settings.MEDIA_ROOT, 'qrcode'), name)
        with open (file, 'rb') as imagefile:
            qr.base64 = base64.b64encode (imagefile.read ())
        qr.save ()


@receiver (post_save, sender = PressureReport)
def send_sms (sender, instance = None, created = False, **kwargs):
    if created:
        r = requests.get ('http://www.freesms4us.com/kirimsms.php', params = {
            'user': 'ronaldsumbayak',
            'pass': 'sumbayak611',
            'isi': instance.body,
            'no': instance.nomor,
            'return': 'json'
        })
    
        response = json.loads (r.text)
        print (r.text)
        if not response['Status'] == 'Sukses':
            return HttpResponse (json.loads ('{"detail": "gagal terkirim"}'), status = 500)
        return HttpResponse (json.loads ('{"detail": "sukses"}'), status = 200)
