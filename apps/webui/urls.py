#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import os
from django.conf.urls.defaults import patterns, include

from apps.mctc.models.general import Case
from apps.webui.forms.general import CaseForm

urlpatterns = patterns('',
    (r'^$', "apps.webui.views.general.dashboard"),

    (r'^search/$', "apps.webui.views.general.search_view"),
    (r'^district/$', "apps.webui.views.general.district_view"),    
    (r'^providers/$', "apps.webui.views.general.provider_list"),    
    (r'^provider/view/(?P<object_id>\d+)/$', "apps.webui.views.general.provider_view"),        
    
    (r'^case/(?P<object_id>\d+)/$', "apps.webui.views.general.case_view"),
    
    (r'^case/edit/(?P<object_id>\d+)/$', "django.views.generic.create_update.update_object", {
        "template_name": "caseedit.html",
        "form_class": CaseForm
    }),
    
    (r'^', include('malnutrition.ui.urls')),
)
