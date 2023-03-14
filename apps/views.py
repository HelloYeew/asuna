import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.forms import CreateProjectForm, UploadKeyRenewConfirmationForm, AddPermissionForm, EditPermissionForm
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
            project.creator = request.user
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
    all_coverage = CoverageSummary.objects.filter(project_id=project_id).order_by('-date')
    # Get all coverage for graph (get the last 10 coverage and reverse it)
    all_coverage_graph = CoverageSummary.objects.filter(project_id=project_id).order_by('-date')[:10][::-1]

    # Create statistics
    statistics = {
        'Total reports': len(all_coverage),
        'Average': f"{round(CoverageSummary.objects.filter(project_id=project_id).aggregate(Avg('coverage'))['coverage__avg'], 2)}%" if len(all_coverage) > 0 else 'Not enough data',
        'Average (last 30 days)': f"{round(CoverageSummary.objects.filter(project_id=project_id, date__gte=timezone.now() - timezone.timedelta(days=30)).aggregate(Avg('coverage'))['coverage__avg'], 2)}%" if len(all_coverage) > 0 else 'Not enough data',
        'Highest': f"{round(CoverageSummary.objects.filter(project_id=project_id).order_by('-coverage')[0].coverage, 2)}% ({CoverageSummary.objects.filter(project_id=project_id).order_by('-coverage')[0].date.strftime('%Y-%m-%d %H:%M:%S')})" if len(all_coverage) > 0 else 'Not enough data',
        'Lowest': f"{round(CoverageSummary.objects.filter(project_id=project_id).order_by('coverage')[0].coverage, 2)}% ({CoverageSummary.objects.filter(project_id=project_id).order_by('coverage')[0].date.strftime('%Y-%m-%d %H:%M:%S')})" if len(all_coverage) > 0 else 'Not enough data',
        'Last report': f"{all_coverage[0].date.strftime('%Y-%m-%d %H:%M:%S')} ({round(all_coverage[0].coverage, 2)}%)" if len(all_coverage) > 0 else 'No reports'
    }
    return render(request, 'apps/project/detail.html', {
        'project': project,
        'project_access': project_access,
        'not_setup_key': not_setup_key,
        'all_coverage': all_coverage,
        'all_coverage_graph': all_coverage_graph,
        'statistics': statistics
    })


@login_required
def project_manage_permissions(request, project_id):
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
    all_project_access = ProjectAccess.objects.filter(project_id=project_id)
    return render(request, 'apps/project/manage_permissions.html', {
        'project': project,
        'project_access': project_access,
        'all_project_access': all_project_access
    })


@login_required
def project_add_permission(request, project_id):
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
        form = AddPermissionForm(request.POST, project=project)
        if form.is_valid():
            ProjectAccess.objects.create(
                project=project,
                user=User.objects.get(username=form.cleaned_data['username']),
                access_option=form.cleaned_data['permission']
            )
            messages.success(request, 'Permission added successfully!')
            return redirect('apps_project_manage_permissions', project_id=project.id)
    else:
        form = AddPermissionForm(project=project)
    return render(request, 'apps/project/add_permission.html', {
        'project': project,
        'project_access': project_access,
        'form': form
    })


@login_required
def project_edit_permission(request, project_id, project_access_id):
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
    permission = ProjectAccess.objects.filter(id=project_access_id).first()
    if permission.user == project.creator:
        messages.error(request, 'You can not edit permission of project creator!')
        return redirect('apps_project_manage_permissions', project_id=project.id)

    # Check project action setup status
    if request.method == 'POST':
        form = EditPermissionForm(request.POST, instance=permission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Permission updated successfully!')
            return redirect('apps_project_manage_permissions', project_id=project.id)
    else:
        form = EditPermissionForm(instance=permission)
    return render(request, 'apps/project/edit_permission.html', {
        'project': project,
        'project_access': project_access,
        'permission': permission,
        'form': form
    })


@login_required
def project_delete_permission(request, project_id, project_access_id):
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
    permission = ProjectAccess.objects.filter(id=project_access_id).first()
    if permission.user == project.creator:
        messages.error(request, 'You can not delete permission of project creator!')
        return redirect('apps_project_manage_permissions', project_id=project.id)

    permission.delete()
    messages.success(request, 'Permission deleted successfully!')
    return redirect('apps_project_manage_permissions', project_id=project.id)


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
        'full_report': full_report[0] if full_report else None,
        'full_report_json': dict(full_report[0].raw_detail) if full_report else None
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
