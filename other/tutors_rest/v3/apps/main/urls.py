"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

v1 = [
    path('snippets/', views.SnippetList.as_view()),
    path('snippets/<int:pk>/', views.SnippetDetail.as_view()),
]

v2 = [
    path('snippets/', views.snippet_list),
    path('snippets/<int:pk>/', views.snippet_detail),
]

v3 = [
    path('snippets/', views.SnippetListV2.as_view()),
    path('snippets/<int:pk>/', views.SnippetDetailV2.as_view()),
]

v4 = [
    path('snippets/', views.SnippetListV3.as_view()),
    path('snippets/<int:pk>/', views.SnippetDetailV3.as_view()),
]

urlpatterns = [
    path('v1/', include(v2)),
    path('v2/', include(v1)),
    path('v3/', include(v3)),
    path('v4/', include(v4)),
]

urlpatterns = format_suffix_patterns(urlpatterns)


"""
curl -X GET 127.0.0.1:8000/snippets/
curl -X POST 127.0.0.1:8000/snippets/ -d '{"code": "awdwwafef"}'
"""