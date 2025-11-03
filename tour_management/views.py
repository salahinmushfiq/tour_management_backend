from django.http import HttpResponse


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /api/",  # block all API routes
        "Disallow: /admin/",  # optional: block admin
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
