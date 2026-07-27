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

import logging

from cliff import lister

from blazarclient import command


class ListFlavorInstanceAvailability(command.BlazarCommand, lister.Lister):
    """List availability slots for Nova flavors."""
    resource = 'flavor_instance'
    log = logging.getLogger(__name__ + '.ListFlavorInstanceAvailability')
    list_columns = ['flavor_id', 'start', 'end', 'available', 'total']

    def get_parser(self, prog_name):
        parser = super(ListFlavorInstanceAvailability, self).get_parser(
            prog_name)
        parser.add_argument(
            'flavor_id',
            metavar='FLAVOR_ID',
            nargs='?',
            default=None,
            help='Nova flavor UUID to check availability for (default: all flavors)'
        )
        parser.add_argument(
            '--start-date',
            metavar='<start_date>',
            default=None,
            help="Start of the availability window (format: 'YYYY-MM-DD HH:MM',"
                 " default: now)"
        )
        parser.add_argument(
            '--end-date',
            metavar='<end_date>',
            default=None,
            help="End of the availability window (format: 'YYYY-MM-DD HH:MM',"
                 " default: 30 days from start)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        blazar_client = self.get_client()
        result = blazar_client.flavor_instance.get_availability(
            flavor_id=parsed_args.flavor_id,
            start_date=parsed_args.start_date,
            end_date=parsed_args.end_date,
        )
        flavor_results = result.get('flavor_instances', [])
        columns = self.list_columns
        rows = (
            (fr['flavor_id'], seg['start'], seg['end'],
             seg['available'], seg['total'])
            for fr in flavor_results
            for seg in fr.get('availability', [])
        )
        return columns, rows
