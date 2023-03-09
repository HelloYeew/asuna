from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


def homepage(request):
    return render(request, 'pages/home.html')


@require_GET
def robots_txt(request):
    """
    Return the robots.txt file to tell the search engine crawlers not to index the site.
    """
    lines = [
        # Disallowed all robots in media folder
        "User-agent: *",
        "Disallow: /media/*",
        "Disallow: /static/*",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
