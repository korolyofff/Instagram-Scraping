"""IG_Scraper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from scraper.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scrape/', scrape, name='main page'),
    path('documentation/', documentation, name='documentation'),
    path('hashtag?collector/', HashtagView.as_view(), name='hashtag'),
    path('follower?collector/', FollowersView.as_view(), name='follower'),
    path('following?collector/', FollowingView.as_view(), name='following'),
    path('to?excel/', ToExcelView.as_view(), name= 'to_excel')
]
