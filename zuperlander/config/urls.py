# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

import landinator
from landinator.views import DynaformChoicesRelatedFieldViewAJAX, DynaformViewAJAX

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    url(r'^nested_admin/', include('nested_admin.urls')),

    # Your stuff: custom urls includes go here
    url(r'^landing/', include('landinator.urls', namespace="landinator", app_name='landinator')),

    # facebook stuff
    url(r'^leadmanager/', landinator.views.leads, name='facebook_action'),
    url(r'^platformconnect/', landinator.views.platform, name='connect_action'),
    url(r'^privacy/', landinator.views.privacy, name='privacy_action'),

    # DinaForm stuff
    url(r'^formsubmit/(?P<slug>[\w\-\_\.]+)/(?P<pk>\d+)/?$', DynaformViewAJAX.as_view(), name='dynaform_action'),
    url(r'^(?P<field_pk>\d+)/(?P<related_field_pk>\d+)/(?P<pk>\d+)/?$', DynaformChoicesRelatedFieldViewAJAX.as_view(), name='dynaform_choices_related_queryset'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

