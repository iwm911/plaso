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
"""Tests for the Apple account plist plugin."""

import unittest

# pylint: disable=unused-import
from plaso.formatters import plist as plist_formatter
from plaso.lib import event
from plaso.parsers import plist
from plaso.parsers.plist_plugins import appleaccount
from plaso.parsers.plist_plugins import test_lib


class AppleAccountPluginTest(test_lib.PlistPluginTestCase):
  """Tests for the Apple account plist plugin."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._plugin = appleaccount.AppleAccountPlugin(None)
    self._parser = plist.PlistParser(event.PreprocessObject(), None)

  def testProcess(self):
    """Tests the Process function."""
    plist_file = (u'com.apple.coreservices.appleidauthenticationinfo.'
                  u'ABC0ABC1-ABC0-ABC0-ABC0-ABC0ABC1ABC2.plist')
    test_file = self._GetTestFilePath([plist_file])
    plist_name = plist_file
    events = self._ParsePlistFileWithPlugin(
        self._parser, self._plugin, test_file, plist_name)
    event_objects = self._GetEventObjects(events)

    self.assertEquals(len(event_objects), 3)

    timestamps = []
    for event_object in event_objects:
      timestamps.append(event_object.timestamp)
    expected_timestamps = frozenset([
        1372106802000000, 1387980032000000, 1387980032000000])
    self.assertTrue(set(timestamps) == expected_timestamps)

    event_object = event_objects[0]
    self.assertEqual(event_object.root, u'/Accounts')
    self.assertEqual(event_object.key, u'email@domain.com')
    expected_desc = (u'Configured Apple account '
                    u'email@domain.com (Joaquin Moreno Garijo)')
    self.assertEqual(event_object.desc, expected_desc)
    expected_string = u'/Accounts/email@domain.com {}'.format(expected_desc)
    expected_short = expected_string[:77] + u'...'
    self._TestGetMessageStrings(
        event_object, expected_string, expected_short)

    event_object = event_objects[1]
    expected_desc = (u'Connected Apple account '
                     u'email@domain.com (Joaquin Moreno Garijo)')
    self.assertEqual(event_object.desc, expected_desc)

    event_object = event_objects[2]
    expected_desc = (u'Last validation Apple account '
                     u'email@domain.com (Joaquin Moreno Garijo)')
    self.assertEqual(event_object.desc, expected_desc)


if __name__ == '__main__':
  unittest.main()
