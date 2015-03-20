# Copyright 2014 Intel Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from blazardashboard.dashboards.project.leases import views as leases_views


urlpatterns = patterns(
    '',
    url(r'^$', leases_views.IndexView.as_view(), name='index'),
    url(r'^calendar/$', leases_views.CalendarView.as_view(), name='calendar'),
    url(r'^calendar.json$', 'blazardashboard.dashboards.project.leases.views.calendar_data_view', name='calendar_data'),
    url(r'^create/$', leases_views.CreateView.as_view(), name='create'),
    url(r'^(?P<lease_id>[^/]+)/$', leases_views.DetailView.as_view(),
        name='detail'),
    url(r'^(?P<lease_id>[^/]+)/update$', leases_views.UpdateView.as_view(),
        name='update'),
)
