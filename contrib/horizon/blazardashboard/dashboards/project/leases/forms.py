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


from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta

from horizon import exceptions
from horizon import forms
from horizon import messages

from blazardashboard import api

import pytz
import logging

logger = logging.getLogger('horizon')


class CreateForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Create New Lease')

    name = forms.CharField(
        label=_('Name'),
        widget=forms.TextInput()
    )

    start_date = forms.DateTimeField(
        label=_('Start Date'),
        help_text=_('Enter date with the format YYYY-MM-DD or leave blank for today'),
        error_messages={
            'invalid': _('Value should be date, formatted YYYY-MM-DD'),
        },
        input_formats=['%Y-%m-%d'],
        widget=forms.DateTimeInput(attrs={'placeholder':'Y-M-D', 'class':'datepicker'}),
        required=False,
    )
    start_time = forms.DateTimeField(
        label=_('Start Time'),
        help_text=_('Enter time with the format HH:MM (24-hour clock) or leave blank for now'),
        error_messages={
            'invalid': _('Value should be time, formatted HH:MM (24-hour clock)'),
        },
        input_formats=['%H:%M'],
        widget=forms.DateTimeInput(attrs={'placeholder':'H:M'}),
        required=False,
    )
    end_date = forms.DateTimeField(
        label=_('End Date'),
        help_text=_('Enter date with the format YYYY-MM-DD or leave blank for tomorrow'),
        error_messages={
            'invalid': _('Value should be date, formatted YYYY-MM-DD'),
        },
        input_formats=['%Y-%m-%d'],
        widget=forms.DateTimeInput(attrs={'placeholder':'Y-M-D', 'class':'datepicker'}),
        required=False,
    )
    end_time = forms.DateTimeField(
        label=_('End Time'),
        help_text=_('Enter time with the format HH:MM (24-hour clock) or leave blank for same time as now'),
        error_messages={
            'invalid': _('Value should be time, formatted HH:MM (24-hour clock)'),
        },
        input_formats=['%H:%M'],
        widget=forms.DateTimeInput(attrs={'placeholder':'H:M'}),
        required=False,
    )
    resource_type = forms.ChoiceField(
        label=_('Resource Type'),
        choices=(
            ('physical:host', _('Physical Host')),
        )
    )
    min_hosts = forms.IntegerField(
        label=_('Minimum Number of Hosts'),
        help_text=_('Enter the minimum number of hosts to reserve.'),
        min_value=1,
        initial=1
    )
    max_hosts = forms.IntegerField(
        label=_('Maximum Number of Hosts'),
        help_text=_('Enter the maximum number of hosts to reserve. Enter the same number as the minimum for an exact number.'),
        min_value=1,
        initial=1
    )
    specific_node = forms.CharField(
        label=_('Reserve Specific Node'),
        help_text=_('To reserve a specific node, enter the node UUID here.'),
        required=False,
    )
    node_type = forms.ChoiceField(
        label=_('Node Type to Reserve'),
        help_text=_('Choose standard compute nodes or heterogenous nodes with '
                    'either more storage space, varied storage devices, GPUs, '
                    'Infiniband, or other specialized hardware. Different '
                    'hardware is available on different sites.'),
        choices=api.blazar.available_nodetypes
    )

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

        localtz = pytz.timezone(
            self.request.session.get('django_timezone', self.request.COOKIES.get('django_timezone', 'UTC')))
        my_now = datetime.now(localtz) + timedelta(minutes=1)
        start_date = my_now.strftime('%Y-%m-%d')
        start_time = my_now.strftime('%H:%M')

        end_date = (my_now + timedelta(hours=24)).strftime('%Y-%m-%d')
        end_time = (my_now + timedelta(hours=24)).strftime('%H:%M')

        self.fields['start_date'].widget.attrs['placeholder'] = "Today"
        self.fields['start_time'].widget.attrs['placeholder'] = "Now"

        self.fields['end_date'].widget.attrs['placeholder'] = "Tomorrow"
        self.fields['end_time'].widget.attrs['placeholder'] = "Same time as now"

    def handle(self, request, data):
        try:
            name = data['name']
            start_datetime = data['start_datetime']
            end_datetime = data['end_datetime']
            start = start_datetime.strftime('%Y-%m-%d %H:%M')
            end = end_datetime.strftime('%Y-%m-%d %H:%M')

            reservations = [
                {
                    'min': data['min_hosts'],
                    'max': data['max_hosts'],
                    'hypervisor_properties': '',
                    'resource_properties': '',
                    'resource_type': data['resource_type'],
                }
            ]

            resource_properties = None

            if data['specific_node']:
                resource_properties = '["=", "$uid", "%s"]' % data['specific_node']

            elif data['node_type'] == 'compute':
                #resource_properties = '["=", "$storage_devices.16.device", "sdq"]'
                resource_properties = '["=", "$node_type", "compute"]'

            elif data['node_type'] == 'storage':
                #resource_properties = '["=", "$storage_devices.16.device", "sdq"]'
                resource_properties = '["=", "$node_type", "storage"]'

            elif data['node_type'] == 'gpu_k80':
                #resource_properties = '["=", "$gpu.gpu_model", "K80"]'
                resource_properties = '["=", "$node_type", "gpu_k80"]'

            elif data['node_type'] == 'gpu_m40':
                #resource_properties = '["=", "$gpu.gpu_model", "M40"]'
                resource_properties = '["=", "$node_type", "gpu_m40"]'

            elif data['node_type'] == 'gpu_p100':
                resource_properties = '["=", "$node_type", "gpu_p100"]'

            elif data['node_type'] == 'storage_hierarchy':
                #resource_properties = '["=", "$main_memory.ram_size", "549755813888"]'
                resource_properties = '["=", "$node_type", "storage_hierarchy"]'

            elif data['node_type'] == 'compute_ib':
                #resource_properties = '["=", "$network_adapters.4.device", "ib0"]'
                resource_properties = '["=", "$node_type", "compute_ib"]'

            elif data['node_type'] == 'fpga':
                resource_properties = '["=", "$node_type", "fpga"]'

            elif data['node_type'] == 'lowpower_xeon':
                resource_properties = '["=", "$node_type", "lowpower_xeon"]'

            elif data['node_type'] == 'atom':
                resource_properties = '["=", "$node_type", "atom"]'

            elif data['node_type'] == 'arm64':
                resource_properties = '["=", "$node_type", "arm64"]'

            if resource_properties is not None:
                reservations[0]['resource_properties'] = resource_properties

            events = []
            lease = api.blazar.lease_create(request, name, start, end, reservations, events)

            # store created_lease_id in session for redirect in view
            request.session['created_lease_id'] = lease.id

            messages.success(request, _("Lease created successfully."))
            return True
        except Exception as e:
            logger.error('Error submitting lease: %s', e)
            exceptions.handle(request, message="An error occurred while creating this lease: %s. Please try again." % e)

    def clean(self):
        cleaned_create_data = super(CreateForm, self).clean()
        localtz = pytz.timezone(self.request.session.get('django_timezone', self.request.COOKIES.get('django_timezone', 'UTC')))

        # convert dates and times to datetime UTC
        start_date = cleaned_create_data.get("start_date")
        start_time = cleaned_create_data.get("start_time")

        if start_date == '' or start_date == None:
            start_date = datetime.now(localtz) + timedelta(minutes=1)

        if start_time == '' or start_time == None:
            start_time = datetime.now(localtz) + timedelta(minutes=1)

        #logger.debug("start date " + start_date.strftime('%Y-%m-%d'))
        #logger.debug("start time " + start_time.strftime('%H:%M'))
        start_datetime = self.prepare_datetimes(start_date, start_time)

        end_date = cleaned_create_data.get("end_date")
        end_time = cleaned_create_data.get("end_time")

        if end_date == '' or end_date == None:
            end_date = datetime.now(localtz) + timedelta(days=1)

        if end_time == '' or end_time == None:
            end_time = datetime.now(localtz) + timedelta(days=1)

        #logger.debug("End date " + end_date.strftime('%Y-%m-%d'))
        #logger.debug("End time " + end_time.strftime('%H:%M'))
        end_datetime = self.prepare_datetimes(end_date, end_time)

        logger.debug("Creating lease with default start time of "
                     + start_date.strftime('%Y-%m-%d') + " " + start_time.strftime('%H:%M')
                     + " and end time of " + end_date.strftime('%Y-%m-%d') + " " + end_time.strftime('%H:%M'))

        if start_datetime < datetime.now(pytz.utc):
            raise forms.ValidationError("Start date must be in the future")

        if start_datetime >= end_datetime:
            raise forms.ValidationError("Start date and time must be before end date and time")

        cleaned_create_data['start_datetime'] = start_datetime
        cleaned_create_data['end_datetime'] = end_datetime

        # check for name conflicts
        leases = api.blazar.lease_list(self.request)

        for lease in leases:
            if lease['name'] == cleaned_create_data.get("name"):
                raise forms.ValidationError("A lease with this name already exists.")

        # check for host availability
        num_hosts = api.blazar.compute_host_available(self.request, start_datetime, end_datetime)
        if cleaned_create_data.get('min_hosts') > num_hosts:
            raise forms.ValidationError("Not enough hosts are available for this reservation (minimum %s requested; %s available). Try adjusting the number of hosts requested or the date range for the reservation." % (cleaned_create_data.get('min_hosts'), num_hosts))

        return cleaned_create_data

    def prepare_datetimes(self, date_val, time_val):
        """
        Ensure the date and time are in user's timezone, then convert to UTC.
        """
        localtz = pytz.timezone(self.request.session.get('django_timezone', self.request.COOKIES.get('django_timezone', 'UTC')))
        datetime_val = date_val.replace(hour=time_val.time().hour, minute=time_val.time().minute, tzinfo=None)
        datetime_val = localtz.localize(datetime_val)
        return datetime_val.astimezone(pytz.utc)

class UpdateForm(forms.SelfHandlingForm):

    class Meta:
        name = _('Update Lease Parameters')

    lease_id = forms.CharField(
        label=_('Lease ID'), widget=forms.widgets.HiddenInput, required=True)
    name = forms.CharField(label=_('Stack Name'), widget=forms.TextInput())
    prolong_for = forms.CharField(
        label=_('Prolong for'),
        widget=forms.TextInput(attrs={'placeholder':
                                      _('Valid suffix are s/h/m/d')}),
        required=False)
    reduce_by = forms.CharField(
        label=_('Reduce by'),
        widget=forms.TextInput(attrs={'placeholder':
                                      ('Valid suffix are s/h/m/d')}),
        required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        #TODO(pafuent): When action is implemented use this code to hide fields
        #initial = kwargs.get('initial', None)
        #if initial:
            #if initial['lease'].action:
                #self.fields['prolong_for'].widget = forms.HiddenInput()
                #self.fields['reduce_by'].widget = forms.HiddenInput()

    def handle(self, request, data):
        lease_id = data.get('lease_id')
        fields = {
            'name': data.get('name'),
            'prolong_for': data.get('prolong_for', None) or None,
            'reduce_by': data.get('reduce_by', None) or None,
        }

        try:
            api.blazar.lease_update(self.request, lease_id=lease_id, **fields)
            messages.success(request, _("Lease update started."))
            return True
        except Exception as e:
            logger.error('Error updating lease: %s', e)
            exceptions.handle(request, message="An error occurred while updating this lease: %s. Please try again." % e)
