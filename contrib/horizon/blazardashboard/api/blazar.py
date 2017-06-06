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

from collections import OrderedDict
import logging

from django.db import connections
from django.utils.translation import ugettext_lazy as _
import six

from climateclient import client as blazar_client
from climateclient import exception as blazar_exception

from openstack_dashboard.api import base


LOG = logging.getLogger(__name__)
LEASE_DATE_FORMAT = "%Y-%m-%d %H:%M"

PRETTY_TYPE_NAMES = OrderedDict([
    ('compute', _('Compute Node (default)')),
    ('storage', _('Storage')),
    ('gpu_k80', _('GPU (K80)')),
    ('gpu_m40', _('GPU (M40)')),
    ('gpu_p100', _('GPU (P100)')),
    ('compute_ib', _('Infiniband Support')),
    ('storage_hierarchy', _('Storage Hierarchy')),
    ('fpga', _('FPGA')),
    ('lowpower_xeon', _('Low power Xeon')),
    ('atom', _('Atom')),
    ('arm64', _('ARM64')),
])


class Lease(base.APIDictWrapper):
    """Represents one Blazar lease."""
    ACTIONS = (CREATE, DELETE, UPDATE, START, STOP
               ) = ('CREATE', 'DELETE', 'UPDATE', 'START', 'STOP')

    STATUSES = (IN_PROGRESS, FAILED, COMPLETE
                ) = ('IN_PROGRESS', 'FAILED', 'COMPLETE')

    _attrs = ['id', 'name', 'start_date', 'end_date', 'user_id', 'project_id',
              'before_end_notification', 'action', 'status', 'status_reason']

    def __init__(self, apiresource):
        super(Lease, self).__init__(apiresource)

    #@property
    #def xxx(self):
        #return self._xxx


def blazarclient(request):
    """Initialization of Blazar client."""

    endpoint = base.url_for(request, 'reservation')
    LOG.debug('blazarclient connection created using token "%s" '
              'and endpoint "%s"' % (request.user.token.id, endpoint))
    return blazar_client.Client(climate_url=endpoint,
                                auth_token=request.user.token.id)


def lease_list(request):
    """List the leases."""
    leases = blazarclient(request).lease.list()
    return [Lease(l) for l in leases]


def lease_get(request, lease_id):
    """Get a lease."""
    lease = blazarclient(request).lease.get(lease_id)
    return Lease(lease)


def lease_create(request, name, start, end, reservations, events):
    """Create a lease."""
    lease = blazarclient(request).lease.create(name, start, end, reservations, events)
    return Lease(lease)


def lease_update(request, lease_id, **kwargs):
    """Update a lease."""
    lease = blazarclient(request).lease.update(lease_id, **kwargs)
    return Lease(lease)


def lease_delete(request, lease_id):
    """Delete a lease."""
    try:
        blazarclient(request).lease.delete(lease_id)
    except blazar_exception.ClimateClientException:
        # XXX This is temporary until we can display a proper error pop-up in
        # Horizon instead of an error page
        pass

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def compute_host_available(request, start_date, end_date):
    """
    Return the number of compute hosts available for reservation for the entire
    specified date range.
    """
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M')
    cursor = connections['blazar'].cursor()
    cursor.execute("""
        select count(*) as available
        from computehosts ch
        where ch.id not in (
            select ch.id
            from computehosts ch
            join computehost_allocations cha on cha.`compute_host_id` = ch.`id`
            join reservations r on r.id = cha.`reservation_id`
            join leases l on l.`id` = r.`lease_id`
            where
                r.deleted="0" and
                ch.deleted="0" and
                ((l.`start_date` > %s and l.`start_date` < %s)
                or (l.`end_date` > %s and l.`end_date` < %s)
                or (l.`start_date` < %s and l.`end_date` > %s))
        )
        """, [start_date_str, end_date_str, start_date_str, end_date_str, start_date_str, end_date_str])
    count = cursor.fetchone()[0]
    return count

def node_in_lease(request, lease_id):
    sql = '''\
    SELECT
        c.hypervisor_hostname
    FROM
        computehost_allocations AS ca
        JOIN computehosts AS c ON c.id = ca.compute_host_id
        JOIN reservations AS r ON r.id = ca.reservation_id
        JOIN leases AS l ON l.id = r.lease_id
    WHERE
        l.id = %s
        AND ca.deleted = '0'
    '''
    sql_args = (lease_id,)

    cursor = connections['blazar'].cursor()
    cursor.execute(sql, sql_args)
    hypervisor_hostnames = dictfetchall(cursor)
    return hypervisor_hostnames

def compute_host_list(request, node_types=False):
    """Return a list of compute hosts available for reservation"""
    cursor = connections['blazar'].cursor()
    cursor.execute('SELECT hypervisor_hostname, vcpus, memory_mb, local_gb, cpu_info, hypervisor_type FROM computehosts WHERE deleted="0"')
    compute_hosts = dictfetchall(cursor)

    if node_types:
        node_types = node_type_map(cursor)
        for ch in compute_hosts:
            ch['node_type'] = node_types.get(ch['hypervisor_hostname'], 'unknown')

    return compute_hosts

def node_type_map(cursor=None):
    if cursor is None:
        cursor = connections['blazar'].cursor()
    sql = '''\
    SELECT ch.hypervisor_hostname AS id, nt.node_type
    FROM blazar.computehosts AS ch
    INNER JOIN (
        SELECT ex.computehost_id AS id, ex.capability_value AS node_type
        FROM blazar.computehost_extra_capabilities AS ex
        INNER JOIN (
            SELECT id, MAX(created_at)
            FROM blazar.computehost_extra_capabilities
            WHERE capability_name = 'node_type' AND deleted = '0'
            GROUP BY computehost_id
        ) AS exl
        ON ex.id = exl.id
    ) AS nt
    ON ch.id = nt.id;
    '''
    cursor.execute(sql)
    node_types = dict(cursor.fetchall())
    return node_types

def reservation_calendar(request):
    """Return a list of all scheduled leases."""
    cursor = connections['blazar'].cursor()
    sql = '''\
    SELECT
        l.name,
        l.project_id,
        l.start_date,
        l.end_date,
        r.status,
        c.hypervisor_hostname
    FROM
        computehost_allocations cha
        JOIN computehosts c ON c.id = cha.compute_host_id
        JOIN reservations r ON r.id = cha.reservation_id
        JOIN leases l ON l.id = r.lease_id
    WHERE
        r.deleted = '0'
        AND c.deleted = '0'
        AND cha.deleted = '0'
    ORDER BY
        start_date,
        project_id;
    '''
    cursor.execute(sql)
    host_reservations = dictfetchall(cursor)

    return host_reservations

def available_nodetypes():
    cursor = connections['blazar'].cursor()
    sql = '''\
    SELECT DISTINCT
        capability_value
    FROM
        computehost_extra_capabilities
    WHERE
        capability_name = 'node_type'
        AND deleted = '0'
    '''
    cursor.execute(sql)
    available = {row[0] for row in cursor.fetchall()}
    choices = [(k, six.text_type(v)) for k, v in PRETTY_TYPE_NAMES.items() if k in available]

    unprettyable = available - set(PRETTY_TYPE_NAMES)
    if unprettyable:
        unprettyable = sorted(unprettyable)
        choices.extend((k, k) for k in unprettyable)
        LOG.debug('New node types without pretty name(s): {}'.format(unprettyable))

    return choices
