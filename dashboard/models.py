from datetime import date

import io
import qrcode
import sys
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver (post_save, sender = User)
def create_auth_token (sender, instance = None, created = False, **kwargs):
    if created:
        Token.objects.create (user = instance)

def save_qrcode (instance, filename):
    print (filename)
    return filename


class Apar (models.Model):
    lokasi       = models.CharField (max_length = 128)
    nomor_lokasi = models.CharField (max_length = 8)
    jenis        = models.CharField (max_length = 8)
    kapasitas    = models.IntegerField ()
    kondisi      = models.IntegerField (default = 0, choices = (
        (-1, "Bad"),
        (0,  "Unknown"),
        (1,  "Good")
    ))
    
    catatan    = models.TextField (max_length = 1024, blank = True, null = True)
    pengisian  = models.DateField (blank = True, null = True)
    pengecekan = models.DateField (blank = True, null = True)
    inspector  = models.ForeignKey (User, blank = True, null = True)
    
    @property
    def is_kadaluarsa (self):
        return date.today ().year - self.pengisian.year > 5
    
    def __str__ (self):
        return "%s (%s)" % (self.lokasi, self.nomor_lokasi)


class QRCode (models.Model):
    apar  = models.ForeignKey (Apar)
    image = models.ImageField (upload_to = 'qrcode')
    
    def __str__ (self):
        return self.apar.__str__ ()


@receiver (post_save, sender = Apar)
def generate_qrcode (sender, instance = None, created = False, **kwargs):
    if created:
        img = qrcode.make (instance.id)
        stream = io.BytesIO ()
        img.save (stream)
        filename = '%s.png' % (instance.id)
        filecontent = InMemoryUploadedFile (stream, None, filename, 'image/png', sys.getsizeof (stream), None)
        qr = QRCode.objects.create (apar = instance)
        qr.image.save (filename, filecontent)
        qr.save ()