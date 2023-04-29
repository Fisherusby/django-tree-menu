from django import views
from django.shortcuts import redirect, render
from django.urls import resolve

from .services import gen_test_menu


def index(request):
    return redirect("example")


def make_menu(request):
    gen_test_menu.gen_example_menus()
    return redirect("example")


class MenuPathViewSet(views.View):
    def get(self, request, menu="index"):
        return render(
            request,
            "example.html",
            context={
                "url": request.path_info,
                "name": '-',
            },
        )


class NamedViewSet(views.View):
    def get(self, request):
        url_name = resolve(request.path_info).url_name
        return render(
            request,
            "example.html",
            context={
                "url": request.path_info,
                "name": url_name,
            }
        )
