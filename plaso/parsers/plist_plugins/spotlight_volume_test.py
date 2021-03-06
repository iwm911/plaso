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
"""Tests for the Spotlight Volume configuration plist plugin."""

import unittest

# pylint: disable=unused-import
from plaso.formatters import plist as plist_formatter
from plaso.lib import event
from plaso.parsers import plist
from plaso.parsers.plist_plugins import spotlight_volume
from plaso.parsers.plist_plugins import test_lib


class SpotlightVolumePluginTest(test_lib.PlistPluginTestCase):
  """Tests for the Spotlight Volume configuration plist plugin."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._plugin = spotlight_volume.SpotlightVolumePlugin(None)
    self._parser = plist.PlistParser(event.PreprocessObject(), None)

  def testProcess(self):
    """Tests the Process function."""
    test_file = self._GetTestFilePath(['VolumeConfiguration.plist'])
    plist_name = 'VolumeConfiguration.plist'
    events = self._ParsePlistFileWithPlugin(
        self._parser, self._plugin, test_file, plist_name)
    event_objects = self._GetEventObjects(events)

    self.assertEquals(len(event_objects), 2)

    timestamps = []
    for event_object in event_objects:
      timestamps.append(event_object.timestamp)
    expected_timestamps = frozenset([
        1372139683000000, 1369657656000000])
    self.assertTrue(set(timestamps) == expected_timestamps)

    event_object = event_objects[0]
    self.assertEqual(event_object.key, u'')
    self.assertEqual(event_object.root, u'/Stores')
    expected_desc = (u'Spotlight Volume 4D4BFEB5-7FE6-4033-AAAA-'
                     u'AAAABBBBCCCCDDDD (/.MobileBackups) activated.')
    self.assertEqual(event_object.desc, expected_desc)
    expected_string = u'/Stores/ {}'.format(expected_desc)
    expected_short = expected_string[:77] + u'...'
    self._TestGetMessageStrings(
        event_object, expected_string, expected_short)


if __name__ == '__main__':
  unittest.main()
