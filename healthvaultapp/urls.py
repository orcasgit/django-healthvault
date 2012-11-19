from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',

    # Authentication
    url(r'^authorize/$',
        views.authorize, name='healthvault-authorize'),
    url(r'^complete/$',
        views.complete, name='healthvault-complete'),
    url(r'^error/$',
        views.error, name='healthvault-error'),
    url(r'^deauthorize/$',
        views.deauthorize, name='healthvault-deauthorize'),
)
