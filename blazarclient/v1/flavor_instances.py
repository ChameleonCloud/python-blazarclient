# Copyright (c) 2024 University of Chicago.
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
# implied. See the License for the specific language governing
# permissions and limitations under the License.

from blazarclient import base


class FlavorInstanceClientManager(base.BaseClientManager):
    """Manager for flavor instance availability requests."""

    def get_availability(self, flavor_id=None, start_date=None, end_date=None):
        """Get slot availability timeline for one or all Nova flavors."""
        query_parts = []
        if flavor_id:
            query_parts.append('flavor_id=%s' % flavor_id)
        if start_date:
            query_parts.append('start_date=%s' % start_date)
        if end_date:
            query_parts.append('end_date=%s' % end_date)
        url = '/flavor-instances/availability'
        if query_parts:
            url += '?' + '&'.join(query_parts)
        resp, body = self.request_manager.get(url)
        return body
