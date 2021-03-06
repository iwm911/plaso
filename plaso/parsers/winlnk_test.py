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
"""Tests for the Windows Shortcut (LNK) parser."""

import unittest

# pylint: disable=unused-import
from plaso.formatters import winlnk as winlnk_formatter
from plaso.lib import event
from plaso.lib import eventdata
from plaso.lib import timelib_test
from plaso.parsers import test_lib
from plaso.parsers import winlnk


class WinLnkParserTest(test_lib.ParserTestCase):
  """Tests for the Windows Shortcut (LNK) parser."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    pre_obj = event.PreprocessObject()
    self._parser = winlnk.WinLnkParser(pre_obj, None)

  def testParse(self):
    """Tests the Parse function."""
    test_file = self._GetTestFilePath(['example.lnk'])
    event_generator = self._ParseFile(self._parser, test_file)
    event_objects = self._GetEventObjects(event_generator)

    # Link information:
    # 	Creation time			: Jul 13, 2009 23:29:02.849131000 UTC
    # 	Modification time		: Jul 14, 2009 01:39:18.220000000 UTC
    # 	Access time			: Jul 13, 2009 23:29:02.849131000 UTC
    # 	Description			: @%windir%\system32\migwiz\wet.dll,-590
    # 	Relative path			: .\migwiz\migwiz.exe
    # 	Working directory		: %windir%\system32\migwiz
    # 	Icon location			: %windir%\system32\migwiz\migwiz.exe
    # 	Environment variables location	: %windir%\system32\migwiz\migwiz.exe

    self.assertEqual(len(event_objects), 3)

    # The Last Accessed timestamp.
    event_object = event_objects[0]

    expected_string = u'@%windir%\\system32\\migwiz\\wet.dll,-590'
    self.assertEquals(event_object.description, expected_string)

    expected_string = u'.\\migwiz\\migwiz.exe'
    self.assertEquals(event_object.relative_path, expected_string)

    expected_string = u'%windir%\\system32\\migwiz'
    self.assertEquals(event_object.working_directory, expected_string)

    expected_string = u'%windir%\\system32\\migwiz\\migwiz.exe'
    self.assertEquals(event_object.icon_location, expected_string)
    self.assertEquals(event_object.env_var_location, expected_string)

    expected_timestamp = timelib_test.CopyStringToTimestamp(
        '2009-07-13 23:29:02.849131')
    self.assertEquals(
        event_object.timestamp_desc, eventdata.EventTimestamp.ACCESS_TIME)
    self.assertEquals(event_object.timestamp, expected_timestamp)

    expected_timestamp = timelib_test.CopyStringToTimestamp(
        '2009-07-13 23:29:02.849131')
    event_object = event_objects[1]
    self.assertEquals(
        event_object.timestamp_desc, eventdata.EventTimestamp.CREATION_TIME)
    self.assertEquals(event_object.timestamp, expected_timestamp)

    expected_timestamp = timelib_test.CopyStringToTimestamp(
        '2009-07-14 01:39:18.220000')
    event_object = event_objects[2]
    self.assertEquals(
        event_object.timestamp_desc, eventdata.EventTimestamp.MODIFICATION_TIME)
    self.assertEquals(event_object.timestamp, expected_timestamp)

    expected_msg = (
        u'[@%windir%\\system32\\migwiz\\wet.dll,-590] '
        u'File size: 544768 '
        u'File attribute flags: 0x00000020 '
        u'env location: %windir%\\system32\\migwiz\\migwiz.exe '
        u'Relative path: .\\migwiz\\migwiz.exe '
        u'Working dir: %windir%\\system32\\migwiz '
        u'Icon location: %windir%\\system32\\migwiz\\migwiz.exe')

    expected_msg_short = (
        u'[@%windir%\\system32\\migwiz\\wet.dll,-590]')

    self._TestGetMessageStrings(event_object, expected_msg, expected_msg_short)


if __name__ == '__main__':
  unittest.main()
