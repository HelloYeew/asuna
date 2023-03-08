import os

from django.shortcuts import render
from django.urls import reverse
from rest_framework import views, permissions, status
from rest_framework.response import Response

from apps.models import CoverageSummary, CoverageRawDetail, ProjectUploadKey
from apps.utils import random_key
from coverage_apis.serializers import CoverageUploadSerializer


class CoverageUploadView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Upload coverage detail from CI"""
        serializer = CoverageUploadSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            project_upload_key = ProjectUploadKey.objects.filter(key=serializer.validated_data['key'])
            if not project_upload_key:
                return Response({
                    'messages': 'Project upload key not found or invalid'
                }, status=status.HTTP_401_UNAUTHORIZED)
            project = project_upload_key[0].project
            # Create coverage summary
            coverage_summary = CoverageSummary.objects.create(
                project=project,
                name=serializer.validated_data['name'],
                description=serializer.validated_data['description'],
                coverage=serializer.validated_data['percentage']
            )
            # Create coverage raw detail
            upload_folder_name = random_key(8)
            CoverageRawDetail.objects.create(
                summary=coverage_summary,
                folder_name=upload_folder_name,
                raw_detail=serializer.validated_data['coverage']
            )
            # Save all coverage detail file by upload to media folder
            # To folder media/coverage_detail/{project_id}/{upload_folder_name}
            print(request.FILES['file'])
            coverage_detail_file = request.FILES['file']
            # Create folder if not exist
            if not os.path.exists(f'media/coverage_detail/{project.id}/{upload_folder_name}'):
                os.makedirs(f'media/coverage_detail/{project.id}/{upload_folder_name}')
            for coverage_detail_file in request.FILES.getlist('file'):
                with open(f'media/coverage_detail/{project.id}/{upload_folder_name}/{coverage_detail_file.name}', 'wb+') as destination:
                    for chunk in coverage_detail_file.chunks():
                        destination.write(chunk)
            return Response({
                'messages': 'Upload coverage detail success',
                'project': project.name,
                'project_url': self.request.build_absolute_uri(reverse('apps_project_detail', kwargs={'project_id': project.id})),
                'coverage_summary': coverage_summary.id,
                'url': self.request.build_absolute_uri(reverse('apps_coverage_report', kwargs={'project_id': project.id, 'coverage_report_id': coverage_summary.id}))
            }, status=status.HTTP_201_CREATED)
