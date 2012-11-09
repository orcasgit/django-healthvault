from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',

    # Authentication
    url(r'^login/$',
        views.login, name='healthvault-login'),
    url(r'^complete/$',
        views.complete, name='healthvault-complete'),
    url(r'^error/$',
        views.error, name='healthvault-error'),
    url(r'^logout/$',
        views.logout, name='healthvault-logout'),
)
