from django.urls import path

from apps import views

urlpatterns = [
    path('', views.home, name='apps_home'),
    path('project/create', views.create_project, name='apps_create_project'),
    path('project/<int:project_id>', views.project_detail, name='apps_project_detail'),
    path('project/<int:project_id>/upload_key', views.project_upload_key, name='apps_project_upload_key'),
    path('project/<int:project_id>/upload_key/renew', views.project_upload_key_renew, name='apps_project_upload_key_renew'),
    path('project/<int:project_id>/report/<int:coverage_report_id>', views.coverage_report, name='apps_coverage_report')
]
