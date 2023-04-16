from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("example.urls")),
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
]
