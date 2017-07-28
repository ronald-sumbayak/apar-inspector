from django.contrib import admin

from api import models

admin.site.register (models.UserAccessLevel)
admin.site.register (models.Apar)
admin.site.register (models.InspectionReport)
admin.site.register (models.VerificationReport)
admin.site.register (models.PressureReport)
admin.site.register (models.QRCode)
