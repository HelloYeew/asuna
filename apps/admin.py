from django.contrib import admin

from apps.models import Project, ProjectUploadKey, CoverageSummary, CoverageRawDetail, ProjectAccess

admin.site.register(Project)
admin.site.register(ProjectUploadKey)
admin.site.register(ProjectAccess)
admin.site.register(CoverageSummary)
admin.site.register(CoverageRawDetail)
