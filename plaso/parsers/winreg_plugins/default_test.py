#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2012 The Plaso Project Authors.
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
"""Tests for the default Windows Registry plugin."""

import unittest

# pylint: disable=unused-import
from plaso.formatters import winreg as winreg_formatter
from plaso.parsers.winreg_plugins import default
from plaso.parsers.winreg_plugins import test_lib
from plaso.winreg import test_lib as winreg_test_lib


class TestDefaultRegistry(test_lib.RegistryPluginTestCase):
  """Tests for the default Windows Registry plugin."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._plugin = default.DefaultPlugin()

  def testProcess(self):
    """Tests the Process function."""
    key_path = u'\\Microsoft\\Some Windows\\InterestingApp\\MRU'
    values = []
    values.append(winreg_test_lib.TestRegValue(
        'MRUList', 'acb'.encode('utf_16_le'), 1, 123))
    values.append(winreg_test_lib.TestRegValue(
        'a', 'Some random text here'.encode('utf_16_le'), 1, 1892))
    values.append(winreg_test_lib.TestRegValue(
        'b', 'c:/evil.exe'.encode('utf_16_le'), 3, 612))
    values.append(winreg_test_lib.TestRegValue(
        'c', 'C:/looks_legit.exe'.encode('utf_16_le'), 1, 1001))

    winreg_key = winreg_test_lib.TestRegKey(
        key_path, 1346145829002031, values, 1456)

    event_generator = self._ParseKeyWithPlugin(self._plugin, winreg_key)
    event_objects = self._GetEventObjects(event_generator)

    self.assertEquals(len(event_objects), 1)

    event_object = event_objects[0]

    self.assertEquals(event_object.timestamp, 1346145829002031)

    expected_msg = (
        u'[{0:s}] '
        u'MRUList: [REG_SZ] acb '
        u'a: [REG_SZ] Some random text here '
        u'b: [REG_BINARY] '
        u'c: [REG_SZ] C:/looks_legit.exe').format(key_path)

    expected_msg_short = (
        u'[{0:s}] MRUList: [REG_SZ] acb a: [REG_SZ...').format(key_path)

    self._TestGetMessageStrings(event_object, expected_msg, expected_msg_short)


if __name__ == '__main__':
  unittest.main()
