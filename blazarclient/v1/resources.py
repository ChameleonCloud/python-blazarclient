# Copyright (c) 2019 StackHPC Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from blazarclient import base
from blazarclient.i18n import _

import logging
LOG = logging.getLogger(__name__)

class ResourceClientManager(base.BaseClientManager):
    def list_resources(self, sort_by=None):
        resp, body = self.request_manager.get('/resources')
        if sort_by:
            resources = sorted(body, key=lambda l: l[sort_by])
        return body

    def create(self, resource_type, data, **kwargs):
        values = {'data': data}
        values.update(**kwargs)
        resp, body = self.request_manager.post(f'/{resource_type}', body=values)
        return body['resource']

    def get(self, resource_type, resource_id):
        resp, body = self.request_manager.get(
            f'/{resource_type}/{resource_id}')
        return body['resource']

    def update(self, resource_type, res_id, data, extras):
        LOG.info("RESOURCE CLIENT UPDATE")
        if not data and not extras:
            return _('No information to update passed.')
        LOG.info(data)
        LOG.info(extras)
        body = {"data": data, "extras": extras}
        resp, body = self.request_manager.put(
            f'/{resource_type}/{res_id}', body=body
        )
        return body['resource']

    def delete(self, resource_type, resource_id):
        resp, body = self.request_manager.delete(
            f'/{resource_type}/{resource_id}')

    def list(self, resource_type, sort_by=None):
        resp, body = self.request_manager.get(f'/{resource_type}')
        resources = body['resources']
        if sort_by:
            resources = sorted(resources, key=lambda l: l[sort_by])
        return resources

    def get_allocation(self, resource_type, resource_id):
        resp, body = self.request_manager.get(
            f'/{resource_type}/{resource_id}/allocation')
        return body['allocation']

    def list_allocations(self, resource_type, sort_by=None):
        resp, body = self.request_manager.get(f'/{resource_type}/allocations')
        allocations = body['allocations']
        if sort_by:
            allocations = sorted(allocations, key=lambda l: l[sort_by])
        return allocations

    def reallocate(self, resource_type, resource_id, values):
        resp, body = self.request_manager.put(
            f'/{resource_type}/{resource_id}/allocation', body=values)
        return body['allocation']

    def list_capabilities(self, resource_type, detail=False, sort_by=None):
        url = f'/{resource_type}/properties'

        if detail:
            url += '?detail=True'

        resp, body = self.request_manager.get(url)
        resource_properties = body['resource_properties']

        # Values is a reserved word in cliff so need to rename values column.
        if detail:
            for p in resource_properties:
                p['capability_values'] = p['values']
                del p['values']

        if sort_by:
            resource_properties = sorted(resource_properties,
                                         key=lambda l: l[sort_by])
        return resource_properties

    def get_capability(self, resource_type, capability_name):
        resource_property = [
            x for x in self.list_capabilities(resource_type, detail=True)
            if x['property'] == capability_name]

        return {} if not resource_property else resource_property[0]

    def set_capability(self, resource_type, capability_name, private):
        data = {'private': private}
        resp, body = self.request_manager.patch(
            f'/{resource_type}/properties/{capability_name}', body=data)

        return body['resource_property']
