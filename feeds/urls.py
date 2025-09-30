from django.urls import path
from . import api_views

urlpatterns = [
    path('items/', api_views.FeedItemList.as_view(), name='feed_items'),
    path('sources/', api_views.FeedSourceList.as_view(), name='feed_sources'),
]
