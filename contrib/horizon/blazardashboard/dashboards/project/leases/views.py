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

import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from blazardashboard import api
from blazardashboard.dashboards.project.leases import forms as project_forms
from blazardashboard.dashboards.project.leases import tables as project_tables
from blazardashboard.dashboards.project.leases import tabs as project_tabs


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = project_tables.LeasesTable
    template_name = 'project/leases/index.html'

    def get_data(self):
        leases = api.blazar.lease_list(self.request)
        return leases


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.LeaseDetailTabs
    template_name = 'project/leases/detail.html'


class UpdateView(forms.ModalFormView):
    form_class = project_forms.UpdateForm
    template_name = 'project/leases/update.html'
    success_url = reverse_lazy('horizon:project:leases:index')

    def get_initial(self):
        initial = super(UpdateView, self).get_initial()

        initial['lease'] = self.get_object()
        if initial['lease']:
            initial['lease_id'] = initial['lease'].id
            initial['name'] = initial['lease'].name

        return initial

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['lease'] = self.get_object()
        return context

    @memoized.memoized_method
    def get_object(self):
        lease_id = self.kwargs['lease_id']
        try:
            self.lease = api.blazar.lease_get(self.request, lease_id)
        except Exception:
            msg = _("Unable to retrieve lease.")
            redirect = reverse('horizon:project:leases:index')
            exceptions.handle(self.request, msg, redirect=redirect)
        return self.lease