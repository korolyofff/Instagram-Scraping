from django.contrib import admin
from django.urls import path
from scraper.views import *


urlpatterns = [
    path('', scrape),
    path('admin/', admin.site.urls),
    path('scrape/', scrape, name='main page'),
    path('documentation/', documentation, name='documentation'),
    path('hashtag?collector/', HashtagView.as_view(), name='hashtag'),
    path('follower?collector/', FollowersView.as_view(), name='follower'),
    path('following?collector/', FollowingView.as_view(), name='following'),
    path('to?excel/', ToExcelView.as_view(), name= 'to_excel')
]
