# Copyright (c) 2013 Mirantis Inc.
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

import datetime

from climateclient import base
from climateclient import exception
from climateclient.openstack.common.gettextutils import _  # noqa


class LeaseClientManager(base.BaseClientManager):
    """Manager for the lease connected requests."""

    def create(self, name, start, end, reservations, events):
        """Creates lease from values passed."""
        values = {'name': name, 'start_date': start, 'end_date': end,
                  'reservations': reservations, 'events': events}

        return self._create('/leases', values, 'lease')

    def get(self, lease_id):
        """Describes lease specifications such as name, status and locked
        condition.
        """
        return self._get('/leases/%s' % lease_id, 'lease')

    def update(self, lease_id, name=None, prolong_for=None):
        """Update attributes of the lease."""
        values = {}
        if name:
            values['name'] = name
        if prolong_for:
            if prolong_for.endswith('s'):
                coefficient = 1
            elif prolong_for.endswith('m'):
                coefficient = 60
            elif prolong_for.endswith('h'):
                coefficient = 60 * 60
            elif prolong_for.endswith('d'):
                coefficient = 24 * 60 * 60
            else:
                raise exception.ClimateClientException(_("Unsupportable date "
                                                         "format for lease "
                                                         "prolonging."))
            lease = self.get(lease_id)
            cur_end_date = datetime.datetime.strptime(lease['end_date'],
                                                      '%Y-%m-%dT%H:%M:%S.%f')
            seconds = int(prolong_for[:-1]) * coefficient
            delta_sec = datetime.timedelta(seconds=seconds)
            new_end_date = cur_end_date + delta_sec
            values['end_date'] = datetime.datetime.strftime(
                new_end_date, '%Y-%m-%d %H:%M'
            )
        if not values:
            return _('No values to update passed.')
        return self._update('/leases/%s' % lease_id, values,
                            response_key='lease')

    def delete(self, lease_id):
        """Deletes lease with specified ID."""
        self._delete('/leases/%s' % lease_id)

    def list(self):
        """List all leases."""
        return self._get('/leases', 'leases')
