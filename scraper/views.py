from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpRequest
from django.contrib import admin
from django.views.decorators.http import require_http_methods
from .forms import HashtagForm, FollowersForm, FollowingForm
from Scraping_Tool import hashtag_collector
from django.views.generic import CreateView



class HashtagView(View):
    def get(self, request):
        form = HashtagForm(request.GET)
        return render(request, 'hashtag_collector.html', {'form':form})

    def post(self, request):
        form = HashtagForm(request.POST)
        if form.is_valid():
            # hashtag_collector.main()
            hashtags = form.cleaned_data
            print(hashtags)

class FollowersView(View):
    def get(self, request):
        form = FollowersForm(request.GET)
        return render(request, 'follower_collector.html', {'form':form})

    def post(self, request):
        form = FollowersForm(request.POST)
        if form.is_valid():
            # followers_collector.main()
            hashtags = form.cleaned_data
            print(hashtags)

class FollowingView(View):
    def get(self, request):
        form = FollowingForm(request.GET)
        return render(request, 'following_collector.html', {'form':form})

    def post(self, request):
        form = FollowingForm(request.POST)
        if form.is_valid():
            # following_collector.main()
            hashtags = form.cleaned_data
            print(hashtags)

def scrape(request):
    return render(request, 'scrape.html')

def documentation(request):
    return render(request, 'documentation.html')

def follower_collector(request):
    return render(request, 'follower_collector.html')

def following_collector(request):
    return render(request, 'following_collector.html')

