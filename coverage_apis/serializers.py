from rest_framework import serializers

from apps.models import ProjectUploadKey


class CoverageUploadSerializer(serializers.Serializer):
    """Serializer for upload coverage detail from CI

    Attribute:
        key (str): Project upload key
        name (str): Coverage report name (maybe source or some detail)
        description (str): Coverage report description that describe the coverage report
        percentage (float): Coverage percentage
        coverage (json): Coverage detail
        file (file): Bundle of coverage detail file (normally in HTML format)
    """
    key = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    percentage = serializers.FloatField()
    coverage = serializers.JSONField()
    file = serializers.FileField(max_length=None, allow_empty_file=False, use_url=False)
