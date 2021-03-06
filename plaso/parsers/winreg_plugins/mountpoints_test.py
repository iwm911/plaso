#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The Plaso Project Authors.
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
"""Tests for the MountPoints2 Windows Registry plugin."""

import unittest

# pylint: disable=unused-import
from plaso.formatters import winreg as winreg_formatter
from plaso.lib import timelib_test
from plaso.parsers import winreg
from plaso.parsers.winreg_plugins import mountpoints
from plaso.parsers.winreg_plugins import test_lib


class MountPoints2PluginTest(test_lib.RegistryPluginTestCase):
  """Tests for the MountPoints2 Windows Registry plugin."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._plugin = mountpoints.MountPoints2Plugin()

  def testProcess(self):
    """Tests the Process function."""
    test_file = self._GetTestFilePath(['NTUSER-WIN7.DAT'])
    key_path = self._plugin.REG_KEYS[0]
    winreg_key = self._GetKeyFromFile(test_file, key_path)
    event_generator = self._ParseKeyWithPlugin(self._plugin, winreg_key)
    event_objects = self._GetEventObjects(event_generator)

    self.assertEquals(len(event_objects), 5)

    event_object = event_objects[0]

    expected_timestamp = timelib_test.CopyStringToTimestamp(
        '2011-08-23 17:10:14.960960')
    self.assertEquals(event_object.timestamp, expected_timestamp)

    regvalue = event_object.regvalue
    self.assertEquals(regvalue.get('Share_Name'), r'\home\nfury')

    expected_string = (
        u'[{0:s}] Label: Home Drive Remote_Server: controller Share_Name: '
        u'\\home\\nfury Type: Remote Drive Volume: '
        u'##controller#home#nfury').format(key_path)
    expected_string_short = u'{0:s}...'.format(expected_string[0:77])

    self._TestGetMessageStrings(
        event_object, expected_string, expected_string_short)


if __name__ == '__main__':
  unittest.main()
