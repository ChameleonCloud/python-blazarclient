# Copyright (c) 2014 Bull.
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


class DeviceClientManager(base.BaseClientManager):
    """Manager for the Device connected requests."""

    def create(self, name, **kwargs):
        """Creates device from values passed."""
        values = {'name': name}
        values.update(**kwargs)
        resp, body = self.request_manager.post('/devices', body=values)
        return body['device']

    def get(self, device_id):
        """Describe device specifications such as name and details."""
        resp, body = self.request_manager.get('/devices/%s' % device_id)
        return body['device']

    def update(self, device_id, values):
        """Update attributes of the device."""
        if not values:
            return _('No values to update passed.')
        resp, body = self.request_manager.put(
            '/devices/%s' % device_id, body=values
        )
        return body['device']

    def delete(self, device_id):
        """Delete device with specified ID."""
        resp, body = self.request_manager.delete('/devices/%s' % device_id)

    def list(self, sort_by=None):
        """List all devices."""
        resp, body = self.request_manager.get('/devices')
        devices = body['devices']
        if sort_by:
            devices = sorted(devices, key=lambda dev: dev[sort_by])
        return devices

    def get_allocation(self, device_id):
        """Get allocation for device."""
        resp, body = self.request_manager.get(
            '/devices/%s/allocation' % device_id)
        return body['allocation']

    def list_allocations(self, sort_by=None):
        """List allocations for all devices."""
        resp, body = self.request_manager.get('/devices/allocations')
        allocations = body['allocations']
        if sort_by:
            allocations = sorted(allocations, key=lambda alloc: alloc[sort_by])
        return allocations

    def reallocate(self, device_id, values):
        """Reallocate device from leases."""
        resp, body = self.request_manager.put(
            '/devices/%s/allocation' % device_id, body=values)
        return body['allocation']

    def list_properties(self, detail=False, all=False, sort_by=None):
        url = '/devices/properties'

        if detail:
            url += '?detail=True'

        resp, body = self.request_manager.get(url)
        resource_properties = body['resource_properties']

        # Values is a reserved word in cliff so need to rename values column.
        if detail:
            for p in resource_properties:
                p['property_values'] = p['values']
                del p['values']

        if sort_by:
            resource_properties = sorted(resource_properties,
                                         key=lambda prop: prop[sort_by])
        return resource_properties

    def get_property(self, property_name):
        resource_property = [
            x for x in self.list_properties(detail=True)
            if x['property'] == property_name]

        return {} if not resource_property else resource_property[0]

    def set_property(self, property_name, private):
        data = {'private': private}
        resp, body = self.request_manager.patch(
            '/devices/properties/%s' % property_name, body=data)

        return body['resource_property']
