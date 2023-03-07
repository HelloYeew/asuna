import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.forms import CreateProjectForm, UploadKeyRenewConfirmationForm
from apps.models import Project, ProjectAccess, ProjectUploadKey, CoverageSummary, CoverageRawDetail
from apps.utils import random_key


@login_required
def home(request):
    all_project_access = ProjectAccess.objects.filter(user=request.user)
    projects = []
    for project_access in all_project_access:
        projects.append(project_access.project)
    return render(request, 'apps/home.html', {
        'projects': projects
    })


@login_required
def project_list(request):
    all_project_access = ProjectAccess.objects.filter(user=request.user)
    projects = []
    for project_access in all_project_access:
        projects.append(project_access.project)
    return render(request, 'apps/project/list.html', {
        'projects': projects
    })


@login_required
def create_project(request):
    if request.method == 'POST':
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            ProjectAccess.objects.create(
                project=project,
                user=request.user,
                access_option='admin'
            )
            messages.success(request, 'Project created successfully!')
            return redirect('apps_project_detail', project_id=project.id)
    else:
        form = CreateProjectForm()
    return render(request, 'apps/project/create.html', {
        'form': form
    })


@login_required
def project_detail(request, project_id):
    # Check project access
    project = Project.objects.filter(id=project_id)
    if not project:
        return render(request, '404.html', status=404)
    project = project[0]
    project_access = ProjectAccess.objects.filter(project_id=project_id, user=request.user)
    if not project_access:
        return render(request, '404.html', status=404)
    project_access = project_access[0]

    # Check project action setup status
    if project_access.access_option == 'admin' or project_access.access_option == 'write':
        if not ProjectUploadKey.objects.filter(project_id=project_id):
            not_setup_key = True
        else:
            not_setup_key = False
    else:
        not_setup_key = False

    # Get all coverage
    all_coverage = CoverageSummary.objects.filter(project_id=project_id)
    return render(request, 'apps/project/detail.html', {
        'project': project,
        'project_access': project_access,
        'not_setup_key': not_setup_key,
        'all_coverage': all_coverage
    })


@login_required
def edit_project(request, project_id):
    # Check project access
    project = Project.objects.filter(id=project_id)
    if not project:
        return render(request, '404.html', status=404)
    project = project[0]
    project_access = ProjectAccess.objects.filter(project_id=project_id, user=request.user)
    if not project_access:
        return render(request, '404.html', status=404)
    project_access = project_access[0]
    if project_access.access_option != 'admin':
        return render(request, '403.html', status=403)

    # Check project action setup status
    if request.method == 'POST':
        form = CreateProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('apps_project_detail', project_id=project.id)
    else:
        form = CreateProjectForm(instance=project)
    return render(request, 'apps/project/edit.html', {
        'project': project,
        'project_access': project_access,
        'form': form
    })


@login_required
def project_upload_key(request, project_id):
    # Check project access
    project = Project.objects.filter(id=project_id)
    if not project:
        return render(request, '404.html', status=404)
    project = project[0]
    project_access = ProjectAccess.objects.filter(project_id=project_id, user=request.user)
    if not project_access:
        return render(request, '404.html', status=404)
    project_access = project_access[0]
    if project_access.access_option != 'admin' and project_access.access_option != 'write':
        return render(request, '403.html', status=403)

    # Check project action setup status
    upload_key = ProjectUploadKey.objects.filter(project_id=project_id)
    if not upload_key:
        upload_key = ProjectUploadKey.objects.create(
            project=project,
            key=random_key(50)
        )
    else:
        upload_key = upload_key[0]
    # Get all coverage
    all_coverage = CoverageSummary.objects.filter(project_id=project_id)
    return render(request, 'apps/project/upload_key.html', {
        'project': project,
        'project_access': project_access,
        'upload_key': upload_key,
        'all_coverage': all_coverage
    })


@login_required
def project_upload_key_renew(request, project_id):
    # Check project access
    project = Project.objects.filter(id=project_id)
    if not project:
        return render(request, '404.html', status=404)
    project = project[0]
    project_access = ProjectAccess.objects.filter(project_id=project_id, user=request.user)
    if not project_access:
        return render(request, '404.html', status=404)
    project_access = project_access[0]
    if project_access.access_option != 'admin' and project_access.access_option != 'write':
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = UploadKeyRenewConfirmationForm(request.POST, user=request.user)
        if form.is_valid():
            upload_key = ProjectUploadKey.objects.filter(project_id=project_id)
            if not upload_key:
                ProjectUploadKey.objects.create(
                    project=project,
                    key=random_key(50)
                )
            else:
                upload_key = upload_key[0]
                upload_key.key = random_key(50)
                upload_key.setup_at = timezone.now()
                upload_key.save()
            messages.success(request, 'Upload key renewed successfully!')
            return redirect('apps_project_upload_key', project_id=project_id)
    else:
        form = UploadKeyRenewConfirmationForm(user=request.user)
    return render(request, 'apps/project/upload_key_renew.html', {
        'project': project,
        'project_access': project_access,
        'form': form
    })


@login_required
def coverage_report(request, project_id, coverage_report_id):
    # Check project access
    project = Project.objects.filter(id=project_id)
    if not project:
        return render(request, '404.html', status=404)
    project = project[0]
    project_access = ProjectAccess.objects.filter(project_id=project_id, user=request.user)
    if not project_access:
        return render(request, '404.html', status=404)
    project_access = project_access[0]

    # Get coverage
    coverage = CoverageSummary.objects.filter(id=coverage_report_id)
    if not coverage:
        return render(request, '404.html', status=404)
    coverage = coverage[0]
    if coverage.project_id != project_id:
        return render(request, '404.html', status=404)
    full_report = CoverageRawDetail.objects.filter(summary_id=coverage_report_id)
    return render(request, 'apps/project/coverage_report.html', {
        'project': project,
        'project_access': project_access,
        'coverage': coverage,
        'full_report': full_report[0] if full_report else None
    })


@login_required
def coverage_full_report(request, project_id, coverage_report_id):
    # Check project access
    project = Project.objects.filter(id=project_id)
    if not project:
        return render(request, '404.html', status=404)
    project = project[0]
    project_access = ProjectAccess.objects.filter(project_id=project_id, user=request.user)
    if not project_access:
        return render(request, '404.html', status=404)
    project_access = project_access[0]

    # Check compatibility between project and coverage report
    # Coverage report is match with project
    coverage = CoverageSummary.objects.filter(id=coverage_report_id)
    if not coverage:
        return render(request, '404.html', status=404)
    coverage = coverage[0]
    if coverage.project_id != project_id:
        return render(request, '404.html', status=404)

    # Get full report
    full_report = CoverageRawDetail.objects.filter(summary_id=coverage_report_id)
    if not full_report:
        messages.error(request, 'Full report not found!')
        return redirect('apps_coverage_report', project_id=project_id, coverage_report_id=coverage_report_id)
    full_report = full_report[0]
    # Redirect to media file path
    # Get path of media file media/coverage_detail/{project.id}/{upload_folder_name}/index.html
    media_path = os.path.join(settings.MEDIA_ROOT, 'coverage_detail', str(project.id), full_report.folder_name, 'index.html')
    if not os.path.exists(media_path):
        messages.error(request, 'Full report not found!')
        return redirect('apps_coverage_report', project_id=project_id, coverage_report_id=coverage_report_id)
    return redirect(settings.MEDIA_URL + 'coverage_detail/' + str(project.id) + '/' + full_report.folder_name + '/index.html')
