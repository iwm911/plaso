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
"""Contains a formatter for a dynamic output module for plaso."""

import logging
import re

from plaso.lib import errors
from plaso.lib import eventdata
from plaso.lib import output
from plaso.lib import timelib
from plaso.output import helper


class Dynamic(output.FileLogOutputFormatter):
  """Dynamic selection of fields for a separated value output format."""

  FORMAT_ATTRIBUTE_RE = re.compile('{([^}]+)}')

  # A dict containing mappings between "special" attributes and
  # how they should be calculated and presented.
  # They should be documented here:
  #   http://plaso.kiddaland.net/usage/psort/output
  SPECIAL_HANDLING = {
      'date': 'ParseDate',
      'datetime': 'ParseDateTime',
      'description': 'ParseMessage',
      'description_short': 'ParseMessageShort',
      'host': 'ParseHostname',
      'hostname': 'ParseHostname',
      'inode': 'ParseInode',
      'macb': 'ParseMacb',
      'message': 'ParseMessage',
      'message_short': 'ParseMessageShort',
      'source': 'ParseSourceShort',
      'sourcetype': 'ParseSource',
      'source_long': 'ParseSource',
      'tag': 'ParseTag',
      'time': 'ParseTime',
      'timezone': 'ParseZone',
      'type': 'ParseTimestampDescription',
      'user': 'ParseUsername',
      'username': 'ParseUsername',
      'zone': 'ParseZone',
  }

  def ParseTimestampDescription(self, event_object):
    """Return the timestamp description."""
    return getattr(event_object, 'timestamp_desc', '-')

  def ParseTag(self, event_object):
    """Return tagging information."""
    tag = getattr(event_object, 'tag', None)

    if not tag:
      return u'-'

    return u' '.join(tag.tags)

  def ParseSource(self, event_object):
    """Return the source string."""
    event_formatter = eventdata.EventFormatterManager.GetFormatter(event_object)
    if not event_formatter:
      raise errors.NoFormatterFound(
          u'Unable to find no event formatter for: {0:s}.'.format(
              event_object.DATA_TYPE))

    _, source = event_formatter.GetSources(event_object)
    return source

  def ParseSourceShort(self, event_object):
    """Return the source string."""
    event_formatter = eventdata.EventFormatterManager.GetFormatter(event_object)
    if not event_formatter:
      raise errors.NoFormatterFound(
          u'Unable to find no event formatter for: {0:s}.'.format(
              event_object.DATA_TYPE))

    source, _ = event_formatter.GetSources(event_object)
    return source

  def ParseZone(self, _):
    """Return a timezone."""
    return self.zone

  def ParseDate(self, event_object):
    """Return a date string from a timestamp value."""
    date_use = timelib.Timestamp.CopyToDatetime(
        event_object.timestamp, self.zone)
    return u'{0:04d}-{1:02d}-{2:02d}'.format(
        date_use.year, date_use.month, date_use.day)

  def ParseDateTime(self, event_object):
    """Return a datetime object from a timestamp, in an ISO format."""
    return timelib.Timestamp.CopyToIsoFormat(
        event_object.timestamp, timezone=self.zone)

  def ParseTime(self, event_object):
    """Return a timestamp string from an integer timestamp value."""
    date_use = timelib.Timestamp.CopyToDatetime(
        event_object.timestamp, self.zone)
    return u'{0:02d}:{1:02d}:{2:02d}'.format(
        date_use.hour, date_use.minute, date_use.second)

  def ParseHostname(self, event_object):
    """Return a hostname."""
    hostname = getattr(event_object, 'hostname', '')
    if self.store:
      if not hostname:
        hostname = self._hostnames.get(event_object.store_number, '-')

    return hostname

  # TODO: move this into a base output class.
  def ParseUsername(self, event_object):
    """Return the username."""
    username = getattr(event_object, 'username', '-')
    if self.store:
      pre_obj = self._preprocesses.get(event_object.store_number)
      check_user = pre_obj.GetUsernameById(username)

      if check_user != '-':
        username = check_user

    if username == '-' and hasattr(event_object, 'user_sid'):
      return pre_obj.GetUsernameById(
          getattr(event_object, 'user_sid', '-'))

    return username

  def ParseMessage(self, event_object):
    """Return the message string from the EventObject.

    Args:
      event_object: The event object (EventObject).

    Raises:
      errors.NoFormatterFound: If no formatter for that event is found.
    """
    event_formatter = eventdata.EventFormatterManager.GetFormatter(event_object)
    if not event_formatter:
      raise errors.NoFormatterFound(
          u'Unable to find no event formatter for: {0:s}.'.format(
              event_object.DATA_TYPE))

    msg, _ = event_formatter.GetMessages(event_object)
    return msg

  def ParseMessageShort(self, event_object):
    """Return the message string from the EventObject.

    Args:
      event_object: The event object (EventObject).

    Raises:
      errors.NoFormatterFound: If no formatter for that event is found.
    """
    event_formatter = eventdata.EventFormatterManager.GetFormatter(event_object)
    if not event_formatter:
      raise errors.NoFormatterFound(
          u'Unable to find no event formatter for: {0:s}.'.format(
              event_object.DATA_TYPE))

    _, msg_short = event_formatter.GetMessages(event_object)
    return msg_short

  def ParseInode(self, event_object):
    """Return an inode number."""
    inode = getattr(event_object, 'inode', '-')
    if inode == '-':
      if hasattr(event_object, 'pathspec') and hasattr(
          event_object.pathspec, 'image_inode'):
        inode = event_object.pathspec.image_inode

    return inode

  def ParseMacb(self, event_object):
    """Return a legacy MACB representation."""
    return helper.GetLegacy(event_object)

  def Start(self):
    """Returns a header for the output."""
    # Start by finding out which fields are to be used.
    self.fields = []

    if self._filter:
      self.fields = self._filter.fields
      self.separator = self._filter.separator
    else:
      self.separator = u','

    if not self.fields:
      # TODO: Evaluate which fields should be included by default.
      self.fields = [
          'datetime', 'timestamp_desc', 'source', 'source_long',
          'message', 'parser', 'display_name', 'tag', 'store_number',
          'store_index']

    if self.store:
      self._hostnames = helper.BuildHostDict(self.store)
      self._preprocesses = {}
      for info in self.store.GetStorageInformation():
        if hasattr(info, 'store_range'):
          for store_number in range(info.store_range[0], info.store_range[1]):
            self._preprocesses[store_number] = info

    self.filehandle.WriteLine('{0:s}\n'.format(
        self.separator.join(self.fields)))

  def WriteEvent(self, event_object):
    """Write a single event."""
    try:
      self.EventBody(event_object)
    except errors.NoFormatterFound:
      logging.error(u'Unable to output line, no formatter found.')
      logging.error(event_object)

  def EventBody(self, event_object):
    """Formats data as "dynamic" CSV and writes to the filehandle."""
    row = []
    for field in self.fields:
      has_call_back = self.SPECIAL_HANDLING.get(field, None)
      call_back = None
      if has_call_back:
        call_back = getattr(self, has_call_back, None)

      if call_back:
        row.append(call_back(event_object))
      else:
        row.append(getattr(event_object, field, u'-'))

    out_write = u'{0:s}\n'.format(
        self.separator.join(unicode(x).replace(
            self.separator, u' ') for x in row))
    self.filehandle.WriteLine(out_write)

