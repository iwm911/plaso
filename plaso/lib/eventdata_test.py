#!/usr/bin/python
#
# -*- coding: utf-8 -*-
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
"""This file contains a unit test for the EventFilter."""

import unittest

from plaso.lib import event_test
from plaso.lib import eventdata
# pylint: disable=unused-import
from plaso.formatters import winreg


class TestEvent1Formatter(eventdata.EventFormatter):
  """Test event 1 formatter."""
  DATA_TYPE = 'test:event1'
  FORMAT_STRING = u'{text}'

  SOURCE_SHORT = 'FILE'
  SOURCE_LONG = 'Weird Log File'


class WrongEventFormatter(eventdata.EventFormatter):
  """A simple event formatter."""
  DATA_TYPE = 'test:wrong'
  FORMAT_STRING = u'This format string does not match {body}.'

  SOURCE_SHORT = 'FILE'
  SOURCE_LONG = 'Weird Log File'


class EventFormatterUnitTest(unittest.TestCase):
  """The unit test for the event formatter."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self.event_objects = event_test.GetEventObjects()

  def GetCSVLine(self, event_object):
    """Takes an EventObject and prints out a simple CSV line from it."""
    get_sources = eventdata.EventFormatterManager.GetSourceStrings
    try:
      msg, _ = eventdata.EventFormatterManager.GetMessageStrings(event_object)
      source_short, source_long = get_sources(event_object)
    except KeyError:
      print event_object.GetAttributes()
    return u'{0:d},{1:s},{2:s},{3:s}'.format(
        event_object.timestamp, source_short, source_long, msg)

  def testInitialization(self):
    """Test the initialization."""
    self.assertTrue(TestEvent1Formatter())

  def testAttributes(self):
    """Test if we can read the event attributes correctly."""
    events = {}
    for event_object in self.event_objects:
      events[self.GetCSVLine(event_object)] = True

    self.assertIn((
        u'1334961526929596,REG,UNKNOWN key,[MY AutoRun key] Run: '
        u'c:/Temp/evil.exe'), events)

    self.assertIn(
        (u'1334966206929596,REG,UNKNOWN key,[//HKCU/Secret/EvilEmpire/'
         u'Malicious_key] Value: REGALERT: send all the exes to the other '
         u'world'), events)
    self.assertIn((u'1334940286000000,REG,UNKNOWN key,[//HKCU/Windows'
                   u'/Normal] Value: run all the benign stuff'), events)
    self.assertIn((u'1335781787929596,FILE,Weird Log File,This log line reads '
                   u'ohh so much.'), events)
    self.assertIn((u'1335781787929596,FILE,Weird Log File,Nothing of interest'
                   u' here, move on.'), events)
    self.assertIn((u'1335791207939596,FILE,Weird Log File,Mr. Evil just logged'
                   u' into the machine and got root.'), events)

  def testTextBasedEvent(self):
    """Test a text based event."""
    for event_object in self.event_objects:
      source_short, _ = eventdata.EventFormatterManager.GetSourceStrings(
          event_object)
      if source_short == 'LOG':
        msg, msg_short = eventdata.EventFormatterManager.GetMessageStrings(
            event_object)

        self.assertEquals(msg, (
            u'This is a line by someone not reading the log line properly. And '
            u'since this log line exceeds the accepted 80 chars it will be '
            u'shortened.'))
        self.assertEquals(msg_short, (
            u'This is a line by someone not reading the log line properly. '
            u'And since this l...'))


class ConditionalTestEvent1(event_test.TestEvent1):
  DATA_TYPE = 'test:conditional_event1'


class ConditionalTestEvent1Formatter(eventdata.ConditionalEventFormatter):
  """Test event 1 conditional (event) formatter."""
  DATA_TYPE = 'test:conditional_event1'
  FORMAT_STRING_PIECES = [
      u'Description: {description}',
      u'Comment',
      u'Value: 0x{numeric:02x}',
      u'Optional: {optional}',
      u'Text: {text}']

  SOURCE_SHORT = 'LOG'
  SOURCE_LONG = 'Some Text File.'


class BrokenConditionalEventFormatter(eventdata.ConditionalEventFormatter):
  """A broken conditional event formatter."""
  DATA_TYPE = 'test:broken_conditional'
  FORMAT_STRING_PIECES = [u'{too} {many} formatting placeholders']

  SOURCE_SHORT = 'LOG'
  SOURCE_LONG = 'Some Text File.'


class ConditionalEventFormatterUnitTest(unittest.TestCase):
  """The unit test for the conditional event formatter."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self.event_object = ConditionalTestEvent1(1335791207939596, {
        'numeric': 12, 'description': 'this is beyond words',
        'text': 'but we\'re still trying to say something about the event'})

  def testInitialization(self):
    """Test the initialization."""
    self.assertTrue(ConditionalTestEvent1Formatter())
    with self.assertRaises(RuntimeError):
      BrokenConditionalEventFormatter()

  def testGetMessages(self):
    """Test get messages."""
    event_formatter = ConditionalTestEvent1Formatter()
    msg, _ = event_formatter.GetMessages(self.event_object)

    expected_msg = (
        u'Description: this is beyond words Comment Value: 0x0c '
        u'Text: but we\'re still trying to say something about the event')
    self.assertEquals(msg, expected_msg)


if __name__ == '__main__':
  unittest.main()
