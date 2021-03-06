#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The Plaso Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This file contains a default plist plugin in Plaso."""

from plaso.events import plist_event
from plaso.parsers.plist_plugins import interface


class BluetoothPlugin(interface.PlistPlugin):
  """Basic plugin to extract interesting bluetooth related keys."""

  NAME = 'plist_bluetooth'

  PLIST_PATH = 'com.apple.bluetooth.plist'
  PLIST_KEYS = frozenset(['DeviceCache', 'PairedDevices'])

  # LastInquiryUpdate = Device connected via Bluetooth Discovery.  Updated
  #   when a device is detected in discovery mode.  E.g. BT headphone power
  #   on.  Pairing is not required for a device to be discovered and cached.
  #
  # LastNameUpdate = When the human name was last set.  Usually done only once
  #   during initial setup.
  #
  # LastServicesUpdate = Time set when device was polled to determine what it
  #   is.  Usually done at setup or manually requested via advanced menu.

  def GetEntries(self, match, **unused_kwargs):
    """Extracts relevant BT entries.

    Yields:
      EventObject objects extracted from the plist.
    """
    root = '/DeviceCache'

    for device, value in match['DeviceCache'].items():
      name = value.get('Name', '')
      if name:
        name = u''.join(('Name:', name))

      if device in match['PairedDevices']:
        desc = 'Paired:True {}'.format(name)
        key = device
        if 'LastInquiryUpdate' in value:
          yield plist_event.PlistEvent(
              root, key, value['LastInquiryUpdate'], desc)

      if value.get('LastInquiryUpdate'):
        desc = u' '.join(filter(None, ('Bluetooth Discovery', name)))
        key = u''.join((device, '/LastInquiryUpdate'))
        yield plist_event.PlistEvent(
            root, key, value['LastInquiryUpdate'], desc)

      if value.get('LastNameUpdate'):
        desc = u' '.join(filter(None, ('Device Name Set', name)))
        key = u''.join((device, '/LastNameUpdate'))
        yield plist_event.PlistEvent(
            root, key, value['LastNameUpdate'], desc)

      if value.get('LastServicesUpdate'):
        desc = desc = u' '.join(filter(None, ('Services Updated', name)))
        key = ''.join((device, '/LastServicesUpdate'))
        yield plist_event.PlistEvent(
            root, key, value['LastServicesUpdate'], desc)
