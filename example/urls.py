from django.urls import path, include
from .views import index, make_menu, NamedViewSet, MenuPathViewSet


urlpatterns = [
    path('', index, name='index'),
    path('make_menu/', make_menu, name='make_menu'),
    path('example/', MenuPathViewSet.as_view(), name='example'),
    path('example/news', NamedViewSet.as_view(), name='news'),
    path('example/news2', NamedViewSet.as_view(), name='news2'),
    path('example/news3', NamedViewSet.as_view(), name='news3'),
    path('example/news4', NamedViewSet.as_view(), name='news4'),
    path('example/news50', NamedViewSet.as_view(), name='news50'),
    path('example/<str:menu>', MenuPathViewSet.as_view(), name='example_path'),
]
