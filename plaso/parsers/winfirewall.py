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
"""Parser for Windows Firewall Log file."""

import logging

from plaso.lib import event
from plaso.lib import eventdata
from plaso.lib import text_parser
from plaso.lib import timelib

import pyparsing
import pytz


class WinFirewallParser(text_parser.PyparsingSingleLineTextParser):
  """Parses the Windows Firewall Log file.

  More information can be read here:
    http://technet.microsoft.com/en-us/library/cc758040(v=ws.10).aspx
  """

  NAME = 'winfirewall'

  # TODO: Add support for custom field names. Currently this parser only
  # supports the default fields, which are:
  #   date time action protocol src-ip dst-ip src-port dst-port size
  #   tcpflags tcpsyn tcpack tcpwin icmptype icmpcode info path

  # Define common structures.
  BLANK = pyparsing.Literal('-')
  WORD = pyparsing.Word(pyparsing.alphanums + '-') | BLANK
  INT = pyparsing.Word(pyparsing.nums, min=1) | BLANK
  IP = (
      text_parser.PyparsingConstants.IPV4_ADDRESS |
      text_parser.PyparsingConstants.IPV6_ADDRESS | BLANK)
  PORT = pyparsing.Word(pyparsing.nums, min=1, max=6) | BLANK

  # Define how a log line should look like.
  LOG_LINE = (
      text_parser.PyparsingConstants.DATE.setResultsName('date') +
      text_parser.PyparsingConstants.TIME.setResultsName('time') +
      WORD.setResultsName('action') + WORD.setResultsName('protocol') +
      IP.setResultsName('source_ip') + IP.setResultsName('dest_ip') +
      PORT.setResultsName('source_port') + INT.setResultsName('dest_port') +
      INT.setResultsName('size') + WORD.setResultsName('flags') +
      INT.setResultsName('tcp_seq') + INT.setResultsName('tcp_ack') +
      INT.setResultsName('tcp_win') + INT.setResultsName('icmp_type') +
      INT.setResultsName('icmp_code') + WORD.setResultsName('info') +
      WORD.setResultsName('path'))

  # Define the available log line structures.
  LINE_STRUCTURES = [
      ('comment', text_parser.PyparsingConstants.COMMENT_LINE_HASH),
      ('logline', LOG_LINE),
  ]

  DATA_TYPE = 'windows:firewall:log_entry'

  def __init__(self, pre_obj, config):
    """Initializes the parser.

    Args:
      pre_obj: pre-parsing object.
      config: configuration object.
    """
    super(WinFirewallParser, self).__init__(pre_obj, config)
    self.version = None
    self.use_local_zone = False
    self.software = None
    self.local_zone = getattr(pre_obj, 'zone', pytz.utc)

  def VerifyStructure(self, line):
    """Verify that this file is a firewall log file."""
    # TODO: Examine other versions of the file format and if this parser should
    # support them.
    if line == '#Version: 1.5':
      return True

    return False

  def ParseRecord(self, key, structure):
    """Parse each record structure and return an EventObject if applicable."""
    if key == 'comment':
      self._ParseCommentRecord(structure)
    elif key == 'logline':
      return self._ParseLogLine(structure)
    else:
      logging.warning(
          u'Unable to parse record, unknown structure: {0:s}'.format(key))

  def _ParseCommentRecord(self, structure):
    """Parse a comment and store appropriate attributes."""
    comment = structure[1]
    if comment.startswith('Version'):
      _, _, self.version = comment.partition(':')
    elif comment.startswith('Software'):
      _, _, self.software = comment.partition(':')
    elif comment.startswith('Time'):
      _, _, time_format = comment.partition(':')
      if 'local' in time_format.lower():
        self.use_local_zone = True

  def _ParseLogLine(self, structure):
    """Parse a single log line and return an EventObject."""
    log_dict = structure.asDict()

    date = log_dict.get('date', None)
    time = log_dict.get('time', None)

    if not (date and time):
      logging.warning('Unable to extract timestamp from Winfirewall logline.')
      return

    year, month, day = date
    hour, minute, second = time
    if self.use_local_zone:
      zone = self.local_zone
    else:
      zone = pytz.utc

    timestamp = timelib.Timestamp.FromTimeParts(
        year, month, day, hour, minute, second, timezone=zone)

    if not timestamp:
      return

    event_object = event.TimestampEvent(
        timestamp, eventdata.EventTimestamp.WRITTEN_TIME, self.DATA_TYPE)

    for key, value in log_dict.items():
      if key in ('time', 'date'):
        continue
      if value == '-':
        continue

      if type(value) is pyparsing.ParseResults:
        print value
        setattr(event_object, key, ''.join(value))
      else:
        try:
          save_value = int(value)
        except ValueError:
          save_value = value

        setattr(event_object, key, save_value)

    return event_object
