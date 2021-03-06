#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The Plaso Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
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
"""Tests for Apple System Log file parser."""

import unittest

# pylint: disable=unused-import
from plaso.formatters import asl as asl_formatter
from plaso.lib import event
from plaso.lib import timelib_test
from plaso.parsers import asl
from plaso.parsers import test_lib


class AslParserTest(test_lib.ParserTestCase):
  """Tests for Apple System Log file parser."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    pre_obj = event.PreprocessObject()
    self._parser = asl.AslParser(pre_obj, None)

  def testParse(self):
    """Tests the Parse function."""
    test_file = self._GetTestFilePath(['applesystemlog.asl'])
    event_generator = self._ParseFile(self._parser, test_file)
    event_objects = self._GetEventObjects(event_generator)

    self.assertEqual(len(event_objects), 2)

    event_object = event_objects[0]

    expected_timestamp = timelib_test.CopyStringToTimestamp(
        '2013-11-25 09:45:35.705481')
    self.assertEqual(event_object.timestamp, expected_timestamp)

    self.assertEqual(event_object.record_position, 442)
    self.assertEqual(event_object.message_id, 101406)
    self.assertEqual(event_object.computer_name, u'DarkTemplar-2.local')
    self.assertEqual(event_object.sender, u'locationd')
    self.assertEqual(event_object.facility, u'com.apple.locationd')
    self.assertEqual(event_object.pid, 69)
    self.assertEqual(event_object.user_sid, u'205')
    self.assertEqual(event_object.group_id, 205)
    self.assertEqual(event_object.read_uid, 205)
    self.assertEqual(event_object.read_gid, 'ALL')
    self.assertEqual(event_object.level, u'WARNING (4)')

    expected_message = (
        u'Incorrect NSStringEncoding value 0x8000100 detected. '
        u'Assuming NSASCIIStringEncoding. Will stop this compatiblity '
        u'mapping behavior in the near future.')

    self.assertEqual(event_object.message, expected_message)

    expected_extra = (
        u'[CFLog Local Time: 2013-11-25 09:45:35.701]'
        u'[CFLog Thread: 1007]'
        u'[Sender_Mach_UUID: 50E1F76A-60FF-368C-B74E-EB48F6D98C51]')

    self.assertEqual(event_object.extra_information, expected_extra)

    expected_msg = (
        u'MessageID: 101406 '
        u'Level: WARNING (4) '
        u'User ID: 205 '
        u'Group ID: 205 '
        u'Read User: 205 '
        u'Read Group: ALL '
        u'Host: DarkTemplar-2.local '
        u'Sender: locationd '
        u'Facility: com.apple.locationd '
        u'Message: {0:s} {1:s}').format(expected_message, expected_extra)

    expected_msg_short = (
        u'Sender: locationd '
        u'Facility: com.apple.locationd')

    self._TestGetMessageStrings(event_object, expected_msg, expected_msg_short)


if __name__ == '__main__':
  unittest.main()
