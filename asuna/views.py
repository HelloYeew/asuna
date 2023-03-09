from django.shortcuts import redirect


def favicon_icon(request):
    return redirect('/static/favicon.ico')
