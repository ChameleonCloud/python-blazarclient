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

import logging

from oslo_serialization import jsonutils

from blazarclient import command
from blazarclient import exception

RESOURCE_ID_PATTERN = '^[0-9]+$'


class ListResources(command.ListCommand):
    resource = "resource"
    log = logging.getLogger(__name__ + '.ListResources')
    list_columns = ['id', 'data']

    def get_parser(self, prog_name):
        parser = super(ListResources, self).get_parser(prog_name)
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource to list',
        )
        parser.add_argument(
            '--sort-by', metavar="<resource_column>",
            help='column name used to sort result',
            default='id'
        )
        return parser

    def args2body(self, parsed_args):
        params = super(ListResources, self).args2body(parsed_args)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        return params


class ShowResource(command.ShowCommand):
    resource = "resource"
    allow_names = False
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowResource')

    def get_parser(self, prog_name):
        parser = super(ShowResource, self).get_parser(prog_name)
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser

    def args2body(self, parsed_args):
        params = super(ShowResource, self).args2body(parsed_args)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        return params


class CreateResource(command.CreateCommand):
    resource = "resource"
    json_indent = 4
    log = logging.getLogger(__name__ + '.CreateResource')

    def get_parser(self, prog_name):
        parser = super(CreateResource, self).get_parser(prog_name)
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        parser.add_argument(
            'data', metavar='DATA',
            help='json data for the resource'
        )
        return parser

    def args2body(self, parsed_args):
        params = super(CreateResource, self).args2body(parsed_args)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        if parsed_args.data:
            params['data'] = jsonutils.loads(parsed_args.data)
        return params


class UpdateResource(command.UpdateCommand):
    resource = 'resource'
    json_indent = 4
    log = logging.getLogger(__name__ + '.UpdateResource')

    def get_parser(self, prog_name):
        parser = super(UpdateResource, self).get_parser(prog_name)
        parser.add_argument(
            '--extra', metavar='<key>=<value>',
            action='append',
            dest='extra_capabilities',
            default=[],
            help='Extra capabilities key/value pairs to update for the resource'
        )
        parser.add_argument(
            '--data', metavar='<data>', dest='data', default=None,
            help='New data JSON object for resource'
        )
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser

    def args2body(self, parsed_args):
        params = {}
        extras = {}
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        params['data'] = parsed_args.data
        if parsed_args.extra_capabilities:
            for capa in parsed_args.extra_capabilities:
                key, _sep, value = capa.partition('=')
                # NOTE(sbauza): multiple copies of the same capability will
                #               result in only the last value to be stored
                extras[key] = value
        params['extras'] = extras
        return params


class DeleteResource(command.DeleteCommand):
    resource = "resource"
    allow_names = False
    log = logging.getLogger(__name__ + '.DeleteResource')

    def get_parser(self, prog_name):
        parser = super(DeleteResource, self).get_parser(prog_name)
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser

    def args2body(self, parsed_args):
        params = super(DeleteResource, self).args2body(parsed_args)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        return params


class ShowResourceAllocation(command.ShowAllocationCommand):
    resource = 'resource'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowResourceAllocation')

    def get_parser(self, prog_name):
        parser = super(ShowResourceAllocation, self).get_parser(prog_name)
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser

    def args2body(self, parsed_args):
        params = super(ShowResourceAllocation, self).args2body(parsed_args)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        return params


class ListResourceAllocations(command.ListAllocationCommand):
    resource = None
    log = logging.getLogger(__name__ + '.ListResourceAllocations')
    list_columns = ['resource_id', 'reservations']

    def get_parser(self, prog_name):
        parser = super(ListResourceAllocations, self).get_parser(prog_name)
        parser.add_argument(
            '--sort-by', metavar="<resource_column>",
            help='column name used to sort result',
            default='resource_id'
        )
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser

    def args2body(self, parsed_args):
        params = super(ListResourceAllocations, self).args2body(parsed_args)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        return params


class ReallocateResource(command.ReallocateCommand):
    resource = "resource"
    json_indent = 4
    log = logging.getLogger(__name__ + '.ReallocateResource')
    id_pattern = RESOURCE_ID_PATTERN

    def get_parser(self, prog_name):
        parser = super(ReallocateResource, self).get_parser(prog_name)
        parser.add_argument(
            '--lease-id',
            help='Lease ID to reallocate resource from.')
        parser.add_argument(
            '--reservation-id',
            help='Reservation ID to reallocate resource from')
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser

    def args2body(self, parsed_args):
        params = {}

        if parsed_args.reservation_id:
            params['reservation_id'] = parsed_args.reservation_id
        elif parsed_args.lease_id:
            params['lease_id'] = parsed_args.lease_id
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")

        return params


class ShowResourceCapability(command.ShowCapabilityCommand):
    resource = 'resource'
    json_indent = 4
    log = logging.getLogger(__name__ + '.ShowResourceCapability')

    def get_parser(self, prog_name):
        parser = super(ShowResourceCapability, self).get_parser(prog_name)
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser

    def args2body(self, parsed_args):
        params = super(ShowResourceCapability, self).args2body(parsed_args)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        return params


class ListResourceCapabilities(command.ListCommand):
    resource = 'resource'
    log = logging.getLogger(__name__ + '.ListResourceCapabilities')
    list_columns = ['property', 'private', 'capability_values']
    list_fn_name = "list_capabilities"

    def args2body(self, parsed_args):
        params = {'detail': parsed_args.detail}
        if parsed_args.sort_by:
            if parsed_args.sort_by in self.list_columns:
                params['sort_by'] = parsed_args.sort_by
            else:
                msg = 'Invalid sort option %s' % parsed_args.sort_by
                raise exception.BlazarClientException(msg)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")

        return params

    def get_parser(self, prog_name):
        parser = super(ListResourceCapabilities, self).get_parser(prog_name)
        parser.add_argument(
            '--detail',
            action='store_true',
            help='Return capabilities with values and attributes.',
            default=False
        )
        parser.add_argument(
            '--sort-by', metavar="<extra_capability_column>",
            help='column name used to sort result',
            default='property'
        )
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser


class UpdateResourceCapability(command.UpdateCapabilityCommand):
    resource = 'resource'
    json_indent = 4
    log = logging.getLogger(__name__ + '.UpdateResourceCapability')
    name_key = 'capability_name'

    def get_parser(self, prog_name):
        parser = super(UpdateResourceCapability, self).get_parser(prog_name)
        parser.add_argument(
            '--resource', metavar="<resource_type>",
            help='resource type to show',
        )
        return parser

    def args2body(self, parsed_args):
        params = super(UpdateResourceCapability, self).args2body(parsed_args)
        if parsed_args.resource:
            self.resource = parsed_args.resource
        else:
            raise exception.BlazarClientException("Resource not specified")
        return params

