from django.shortcuts import render, redirect, HttpResponse
from django.core.paginator import Paginator

from urllib2 import HTTPError
from urllib import quote, urlencode

import argparse
import json
import sys
import urllib
import requests
import math

from .models import Credential

CREDENTIAL = Credential.objects.get(id=1)

API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
SEARCH_LIMIT = 10

def index(request):
    return render(request, 'search/index.html')

def query_api(request):
    term = request.POST['term']
    location = request.POST['location']
    bearer_token = get_bearer_token(API_HOST, TOKEN_PATH)
    response = search(bearer_token, term, location)
    businesses = response.get('businesses')
    paginator = Paginator(businesses, 10)
    # print 'Count:', paginator.count
    # print 'Pages:', paginator.num_pages
    return render(request, 'search/results.html', {'businesses': businesses})

def query_business(request, id):
    business = get_business(id)
    return render(request, 'search/business.html', {'business': business})

def get_bearer_token(host, path):
    url = '{}{}'.format(host, quote(path.encode('utf8')))
    data = urlencode({
        'client_id': CREDENTIAL.client_id,
        'client_secret': CREDENTIAL.client_secret,
        'grant_type': CREDENTIAL.grant_type
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token

def request(host, path, bearer_token, url_params=None):
    url_params = url_params or {}
    url = '{}{}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer {}'.format(bearer_token)
    }
    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()

def search(bearer_token, term, location):
    url_params = {
        'term': 'best+authentic+' + term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)

def get_business(business_id):
    bearer_token = get_bearer_token(API_HOST, TOKEN_PATH)
    business_path = BUSINESS_PATH + business_id
    return request(API_HOST, business_path, bearer_token)
