from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View
from .forms import HashtagForm, FollowersForm, FollowingForm, ToCSVForm
from scraper.scraper_engine import hashtag_collector, followers_collector
from scraper.scraper_engine import following_collector as fc
from scraper import data, toExcel
from .models import LoginData
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import  HttpResponse
from time import sleep

from django.template import  loader
import os

class HashtagView(LoginRequiredMixin, View):
    login_url = '/admin/'

    def get(self, request):
        form = HashtagForm(request.GET)
        return render(request, 'hashtag_collector.html', {'form':form})

    def post(self, request):
        form = HashtagForm(request.POST)
        if form.is_valid():
            login_data = LoginData.objects.get(pk=1)
            info = form.cleaned_data
            hashtag_collector.main(data.parse_hashtags(info['hashtags']), info['private_only'],
                                   info['business_only'], info['email_only'], info['proxy_port'],
                                   info['proxy_host'], login_data.login, login_data.password)
            template = loader.get_template('scrape.html')

            return HttpResponse(template.render())

class FollowersView(LoginRequiredMixin, View):
    login_url = '/admin/'

    def get(self, request):
        form = FollowersForm(request.GET)
        return render(request, 'follower_collector.html', {'form': form})

    def post(self, request):
        form = FollowersForm(request.POST)
        if form.is_valid():
            login_data = LoginData.objects.get(pk=1)
            info = form.cleaned_data
            print(info)
            followers_collector.main(data.parse_profiles(info['profiles']), info['private_only'],
                                   info['business_only'], info['email_only'], info['proxy_port'],
                                   info['proxy_host'], login_data.login, login_data.password)

            template = loader.get_template('scrape.html')

            return HttpResponse(template.render())

class FollowingView(LoginRequiredMixin,View):
    login_url = '/admin/'
    def get(self, request):
        form = FollowingForm(request.GET)
        return render(request, 'following_collector.html', {'form':form})

    def post(self, request):
        form = FollowingForm(request.POST)
        if form.is_valid():
            login_data = LoginData.objects.get(pk=1)
            info = form.cleaned_data
            fc.main(data.parse_profiles(info['profiles']), info['private_only'],
                                     info['business_only'], info['email_only'], info['proxy_port'],
                                     info['proxy_host'],  login_data.login, login_data.password)

            template = loader.get_template('scrape.html')

            return HttpResponse(template.render())

class ToExcelView(LoginRequiredMixin,View):
    login_url = '/admin/'
    def get(self, request):
        form = ToCSVForm()
        return render(request, 'toCSV.html', {'form':form})

    def post(self, request):
        form = ToCSVForm(request.POST)
        if form.is_valid():
            info = form.cleaned_data
            print(info)
            response = toExcel.export_using_filters(info['email_only'], info['subscribed'], info['subscribed_by_you'])
            sleep(3)
            return response


# @login_required(login_url='/admin/')
def scrape(request):
    return render(request, 'scrape.html')

@login_required(login_url='/admin/')
def documentation(request):
    return render(request, 'documentation.html')

