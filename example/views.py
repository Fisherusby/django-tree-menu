from django.shortcuts import render, redirect
from django import views
from django.urls import resolve
from .services import gen_test_menu


def index(request):
    return redirect('example')
    # return render(request, 'index.html')


def make_menu(request):
    gen_test_menu.gen_example_menus()
    return redirect('example')


class MenuPathViewSet(views.View):
    def get(self, request, menu='index'):
        return render(request, 'example.html', context={'menu': f'target to {request.path_info} and has`nt name'})


class NamedViewSet(views.View):
    def get(self, request):
        url_name = resolve(self.request.path_info).url_name
        return render(request, 'example.html', context={'menu': f'named {url_name}'})
