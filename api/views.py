import base64
import io
import json
import xlsxwriter

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api import models, serializers

class UserRetrieve (generics.RetrieveAPIView):
    queryset = models.UserAccessLevel.objects.all ()
    serializer_class = serializers.UserAccessLevelSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

class AparList (generics.ListAPIView):
    queryset = models.Apar.objects.all ()
    serializer_class = serializers.AparSerializer

class AparRetrieve (generics.RetrieveAPIView):
    queryset = models.Apar.objects.all ()
    serializer_class = serializers.AparSerializer
    lookup_url_kwarg = 'id'

class InspectionReportList (generics.ListAPIView):
    queryset = models.InspectionReport.objects.all ()
    serializer_class = serializers.InspectionReportSerializer

class VerificationReportList (generics.ListAPIView):
    queryset = models.VerificationReport.objects.all ()
    serializer_class = serializers.VerificationReportSerializer

class PressureReportList (generics.ListAPIView):
    queryset = models.PressureReport.objects.all ()
    serializer_class = serializers.PressureReportSerializer
    
@api_view (['POST'])
def inspect (request):
    apar = get_object_or_404 (models.Apar, id = request.data['id'])
    inspection = models.InspectionReport.objects.create (
        apar = apar,
        inspector = request.user,
        kondisi = request.data['kondisi'],
        catatan = request.data.get ('catatan')
    )
    serializer = serializers.InspectionReportSerializer (inspection)
    return Response (serializer.data, status = 200)

@api_view (['POST'])
def verify (request):
    inspection = get_object_or_404 (models.InspectionReport, id = request.data['id'])
    verification = models.VerificationReport.objects.create (
        inspection = inspection,
        verificator = request.user,
        status = request.data['status']
    )
    serializer = serializers.VerificationReportSerializer (verification)
    return Response (serializer.data, status = 200)

class ReportCreate (generics.CreateAPIView):
    serializer_class = serializers.PressureReportSerializer

def media (request, filename):
    qr = QRCode.objects.get (apar__id = filename.split ('/')[-1].split ('.')[0])
    return HttpResponse (base64.b64decode (qr.base64), content_type = 'image/png')

def export_to_excel (request):
    output = io.BytesIO ()
    workbook = xlsxwriter.Workbook (output, {'in_memory': True, 'remove_timezone': True})
    worksheet = workbook.add_worksheet ()

    titles_format = workbook.add_format ({'bold': True, 'align': 'center'})
    titles_format.set_bold ()
    titles_format.set_align ('vcenter')
    titles_format.set_align ('center')

    titles = (
        'Lokasi', 'Nomor Lokasi', 'Jenis', 'Kapasitas (Kg)', 'Kadaluarsa',
        'Kondisi', 'Pengecekan Terakhir', 'Catatan'
    )
    worksheet.write_row (0, 0, titles, titles_format)

    datetime_format = workbook.add_format ()
    datetime_format.set_align ('vcenter')
    datetime_format.set_align ('center')
    datetime_format.set_num_format ('d mmmm yyyy')

    for i, apar in enumerate (models.Apar.objects.all ()):
        i = i + 1
        worksheet.write (i, 0, apar.lokasi)
        worksheet.write (i, 1, apar.nomor_lokasi)
        worksheet.write (i, 2, apar.jenis)
        worksheet.write (i, 3, apar.kapasitas)
        worksheet.write (i, 4, apar.kadaluarsa, datetime_format)

        if apar.inspeksi:
            worksheet.write (i, 5, apar.inspeksi.inspection.get_kondisi_display ())
            worksheet.write (i, 6, apar.inspeksi.inspection.waktu_inspeksi, datetime_format)
            worksheet.write (i, 7, apar.inspeksi.inspection.catatan)

    worksheet.set_column (0, 7, None, workbook.add_format ({'valign': 'vcenter'}))
    worksheet.set_column (1, 6, None, workbook.add_format ({'valign': 'vcenter', 'align': 'center'}))
    worksheet.set_column (0, 0, 30)
    worksheet.set_column (1, 5, 15)
    worksheet.set_column (6, 6, 25)
    worksheet.set_column (7, 7, 25, workbook.add_format ({'text_wrap': True}))

    workbook.close ()

    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse (output.getvalue (), content_type = content_type)
    response['Content-Disposition'] = 'attachment; filename=%s_export.xlsx' % 1
    return response
