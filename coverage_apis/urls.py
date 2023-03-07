from django.urls import path

from coverage_apis.views import CoverageUploadView

urlpatterns = [
    path('upload', CoverageUploadView.as_view(), name='api_coverage_upload')
]
