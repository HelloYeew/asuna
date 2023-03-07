from django.contrib.auth.models import User
from django.db import models


ACCESS_OPTIONS = (
    ('read', 'Read'),
    ('write', 'Write'),
    ('admin', 'Admin'),
)


class Project(models.Model):
    """The project model."""
    name = models.CharField(max_length=50)
    description = models.TextField()
    source = models.URLField()

    def __str__(self):
        return self.name


class ProjectUploadKey(models.Model):
    """The key for using in uploading the coverage report."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    key = models.CharField(max_length=50, unique=True)
    setup_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.project.name} upload key'


class ProjectAccess(models.Model):
    """User access management for projects."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_option = models.CharField(max_length=5, choices=ACCESS_OPTIONS)

    def __str__(self):
        return f'{self.project.name} - {self.user.username} - {self.access_option}'


class CoverageSummary(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    coverage = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.project.name} - {self.date}'


class CoverageRawDetail(models.Model):
    summary = models.ForeignKey(CoverageSummary, on_delete=models.CASCADE)
    folder_name = models.CharField(max_length=10, blank=True, null=True)
    raw_detail = models.JSONField(default=dict)

    def __str__(self):
        return f'{self.summary.project.name} - {self.summary.date} - {self.folder_name}'
