from django import forms

class HashtagForm(forms.Form):
    hashtags = forms.CharField(min_length=3, label='Hashtag Filter', required=True)
    email_only = forms.BooleanField(label='Email only',required=False)
    private_only = forms.BooleanField(label='Private only', required=False)
    business_only = forms.BooleanField(label='Business only', required=False)
    proxy_host = forms.CharField(label='Proxy host', required=False)
    proxy_port = forms.IntegerField(label='Proxy port', required=False)

class FollowersForm(forms.Form):
    profile = forms.CharField(min_length=3, label='Profile Filter', required=True)
    email_only = forms.BooleanField(label='Email only', required=False)
    private_only = forms.BooleanField(label='Private only', required=False)
    business_only = forms.BooleanField(label='Business only', required=False)
    proxy_host = forms.CharField(label='Proxy host', required=False)
    proxy_port = forms.IntegerField(label='Proxy port', required=False)

class FollowingForm(forms.Form):
    profile = forms.CharField(min_length=3, label='Profile Filter', required=True)
    email_only = forms.BooleanField(label='Email only', required=False)
    private_only = forms.BooleanField(label='Private only', required=False)
    business_only = forms.BooleanField(label='Business only', required=False)
    proxy_host = forms.CharField(label='Proxy host', required=False)
    proxy_port = forms.IntegerField(label='Proxy port', required=False)