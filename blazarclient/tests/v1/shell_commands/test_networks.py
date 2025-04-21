# Copyright (c) 2018 StackHPC
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

import argparse
from unittest import mock

from blazarclient import shell
from blazarclient import tests
from blazarclient.v1.networks import NetworkClientManager
from blazarclient.v1.shell_commands import networks


class CreateNetworkTest(tests.TestCase):

    def setUp(self):
        super(CreateNetworkTest, self).setUp()
        self.create_network = networks.CreateNetwork(shell.BlazarShell(), mock.Mock())

    def test_args2body(self):
        args = argparse.Namespace(
            network_type='vlan',
            physical_network='physnet1',
            segment_id='1234',
            extra_capabilities=[
                'extra_key1=extra_value1',
                'extra_key2=extra_value2',
            ]
        )

        expected = {
            'network_type': 'vlan',
            'physical_network': 'physnet1',
            'segment_id': '1234',
            'extra_key1': 'extra_value1',
            'extra_key2': 'extra_value2',
        }

        ret = self.create_network.args2body(args)
        self.assertDictEqual(ret, expected)


class UpdateNetworkTest(tests.TestCase):

    def create_update_command(self, list_value):
        mock_network_manager = mock.Mock()
        mock_network_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.network = mock_network_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return networks.UpdateNetwork(blazar_shell, mock.Mock()), mock_network_manager

    def test_update_network(self):
        list_value = [
            {'id': '072c58c0-64ac-467b-b040-9138771e146a', 'networkname': 'network-1'},
            {'id': '072c58c0-64ac-467b-b040-9138771e146a', 'networkname': 'network-2'},
        ]
        update_network, network_manager = self.create_update_command(list_value)
        args = argparse.Namespace(
            id='072c58c0-64ac-467b-b040-9138771e146a',
            extra_capabilities=[
                'key1=value1',
                'key2=value2'
            ])
        expected = {
            'values': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        update_network.run(args)
        network_manager.update.assert_called_once_with('072c58c0-64ac-467b-b040-9138771e146a', **expected)


class UnsetAttributesNetworkTest(tests.TestCase):

    def create_unset_command(self, list_value):
        mock_network_manager = mock.Mock()
        mock_network_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.network = mock_network_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return networks.UnsetAttributeNetwork(
            blazar_shell, mock.Mock()
        ), mock_network_manager

    def test_unset_network(self):
        list_value = [
            {'id': '072c58c0-64ac-467b-b040-9138771e146a', 'networkname': 'network-1'},
            {'id': '072c58c0-64ac-467b-b040-9138771e146b', 'networkname': 'network-2'},
        ]
        unset_network, network_manager = self.create_unset_command(list_value)
        extra_caps = ['key1', 'key2']
        args = argparse.Namespace(
            id='072c58c0-64ac-467b-b040-9138771e146a',
            extra_capabilities=extra_caps,
        )
        expected = {
            'values': {key: None for key in extra_caps}
       }
        unset_network.run(args)
        network_manager.update.assert_called_once_with('072c58c0-64ac-467b-b040-9138771e146a', **expected)

class ShowNetworkTest(tests.TestCase):

    def create_show_command(self, list_value, get_value):
        mock_network_manager = mock.Mock()
        mock_network_manager.list.return_value = list_value
        mock_network_manager.get.return_value = get_value

        mock_client = mock.Mock()
        mock_client.network = mock_network_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return networks.ShowNetwork(blazar_shell, mock.Mock()), mock_network_manager

    def test_show_network(self):
        list_value = [
            {'id': '072c58c0-64ac-467b-b040-9138771e146a'},
            {'id': '072c58c0-64ac-467b-b040-9138771e146b'},
        ]
        get_value = {
            'id': '072c58c0-64ac-467b-b040-9138771e146a'}

        show_network, network_manager = self.create_show_command(list_value,
                                                           get_value)

        args = argparse.Namespace(id='072c58c0-64ac-467b-b040-9138771e146a', formatter="table")
        expected = [('id',), ('072c58c0-64ac-467b-b040-9138771e146a',)]

        ret = show_network.get_data(args)
        self.assertEqual(ret, expected)

        network_manager.get.assert_called_once_with('072c58c0-64ac-467b-b040-9138771e146a')


class DeleteNetworkTest(tests.TestCase):

    def create_delete_command(self, list_value):
        mock_network_manager = mock.Mock()
        mock_network_manager.list.return_value = list_value

        mock_client = mock.Mock()
        mock_client.network = mock_network_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return networks.DeleteNetwork(blazar_shell, mock.Mock()), mock_network_manager

    def test_delete_network(self):
        # ID should be of format of blazarclient.command.UUID_PATTERN
        list_value = [
            {'id': '072c58c0-64ac-467b-b040-9138771e146a', 'networkname': 'network-1'},
            {'id': '072c58c0-64ac-467b-b040-9138771e146b', 'networkname': 'network-2'},
        ]
        delete_network, network_manager = self.create_delete_command(list_value)

        args = argparse.Namespace(id='072c58c0-64ac-467b-b040-9138771e146a')
        delete_network.run(args)

        network_manager.delete.assert_called_once_with('072c58c0-64ac-467b-b040-9138771e146a')

class MockNetworkClientManager(NetworkClientManager):
    def __init__(self):
        self.request_manager = MockRequestManager()

class MockRequestManager:
    def get(self, url):
        return "-", {
            "networks":
            [
                {
                    "id": "256c0f35-b29e-45cb-9931-ea785f415955",
                    "network_type": "vlan",
                    "physical_network": "physnet1",
                    "segment_id": 3008
                },
                {
                    "id": "937ad993-53c6-4055-9802-e8f360f46598",
                    "network_type": "vlan",
                    "physical_network": "physnet1",
                    "segment_id": 3294
                },
                {
                    "id": "d97e5bb4-46e2-4b65-a460-a2d0bb305d29",
                    "network_type": "vlan",
                    "physical_network": "physnet1",
                    "segment_id": 3006
                },
                {
                    "id": "ee5ec1b8-7295-4c56-8f85-4c89317785d9",
                    "network_type": "vlan",
                    "physical_network": "physnet1",
                    "segment_id": 3009
                }
            ]
        }


class ListNetworksTest(tests.TestCase):

    def create_list_command(self):
        mock_network_manager = MockNetworkClientManager()

        mock_client = mock.Mock()
        mock_client.network = mock_network_manager

        blazar_shell = shell.BlazarShell()
        blazar_shell.client = mock_client
        return networks.ListNetworks(blazar_shell, mock.Mock()), mock_network_manager

    def test_list_network_sort_by(self):

        list_network, network_manager = self.create_list_command()
        list_networks_args = argparse.Namespace(
            sort_by='segment_id',
            columns=[],
            formatter="table",
            long=False,
        )
        return_networks = list_network.get_data(list_networks_args)
        segment_id_index = list(return_networks[0]).index('segment_id')
        prev_segment_id = 0
        for network in list(return_networks[1]):
            network_segment_id = network[segment_id_index]
            self.assertLess(prev_segment_id, network_segment_id)
            prev_segment_id = network_segment_id
        # network_manager.list.assert_called_once_with(sort_by='segment_id')
