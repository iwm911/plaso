#!/usr/bin/python
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
"""This file contains a unit test for the binary helper in Plaso."""
import os
import unittest

from plaso.lib import binary


class BinaryTests(unittest.TestCase):
  """A unit test for the binary helper functions."""

  def setUp(self):
    """Set up the needed variables used througout."""
    # String: "þrándur" - uses surrogate pairs to test four byte character
    # decoding.
    self._unicode_string_1 = (
        '\xff\xfe\xfe\x00\x72\x00\xe1\x00\x6E\x00\x64\x00\x75\x00\x72\x00')

    # String: "What\x00is".
    self._ascii_string_1 = (
        '\x57\x00\x68\x00\x61\x00\x74\x00\x00\x00\x69\x00\x73\x00')

    # String: "What is this?".
    self._ascii_string_2 = (
        '\x57\x00\x68\x00\x61\x00\x74\x00\x20\x00\x69\x00\x73\x00'
        '\x20\x00\x74\x00\x68\x00\x69\x00\x73\x00\x3F\x00')

    # Show full diff results, part of TestCase so does not follow our naming
    # conventions.
    self.maxDiff = None

  def testReadUtf16Stream(self):
    """Test reading an UTF-16 stream from a file-like object."""
    path = os.path.join('test_data', 'PING.EXE-B29F6629.pf')
    with open(path, 'rb') as fh:
      # Read a null char terminated string.
      fh.seek(0x10)
      self.assertEquals(binary.ReadUtf16Stream(fh), 'PING.EXE')

      # Read a fixed size string.
      fh.seek(0x27f8)
      expected_string = u'\\DEVICE\\HARDDISKVOLUME'
      string = binary.ReadUtf16Stream(fh, byte_size=44)
      self.assertEquals(string, expected_string)

      fh.seek(0x27f8)
      expected_string = u'\\DEVICE\\HARDDISKVOLUME1'
      string = binary.ReadUtf16Stream(fh, byte_size=46)
      self.assertEquals(string, expected_string)

      # Read another null char terminated string.
      fh.seek(7236)
      self.assertEquals(
          binary.ReadUtf16Stream(fh),
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\NTDLL.DLL')

  def testUt16StreamCopyToString(self):
    """Test copying an UTF-16 formatted byte stream to a string."""
    path = os.path.join('test_data', 'PING.EXE-B29F6629.pf')
    with open(path, 'rb') as fh:
      byte_stream = fh.read()

      # Read a null char terminated string.
      self.assertEquals(
          binary.Ut16StreamCopyToString(byte_stream[0x10:]), 'PING.EXE')

      # Read a fixed size string.
      expected_string = u'\\DEVICE\\HARDDISKVOLUME'
      string = binary.Ut16StreamCopyToString(
          byte_stream[0x27f8:], byte_stream_size=44)
      self.assertEquals(string, expected_string)

      expected_string = u'\\DEVICE\\HARDDISKVOLUME1'
      string = binary.Ut16StreamCopyToString(
          byte_stream[0x27f8:], byte_stream_size=46)
      self.assertEquals(string, expected_string)

      # Read another null char terminated string.
      expected_string = (
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\NTDLL.DLL')

      string = binary.Ut16StreamCopyToString(byte_stream[7236:])
      self.assertEquals(string, expected_string)

  def testArrayOfUt16StreamCopyToString(self):
    """Test copying an array of UTF-16 formatted byte streams to strings."""
    path = os.path.join('test_data', 'PING.EXE-B29F6629.pf')
    with open(path, 'rb') as fh:
      byte_stream = fh.read()

      strings_array = binary.ArrayOfUt16StreamCopyToString(
          byte_stream[0x1c44:], byte_stream_size=2876)
      expected_strings_array = [
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\NTDLL.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\KERNEL32.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\APISETSCHEMA.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\KERNELBASE.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\LOCALE.NLS',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\PING.EXE',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\ADVAPI32.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\MSVCRT.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\SECHOST.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\RPCRT4.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\IPHLPAPI.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\NSI.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\WINNSI.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\USER32.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\GDI32.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\LPK.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\USP10.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\WS2_32.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\IMM32.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\MSCTF.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\EN-US\\PING.EXE.MUI',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\GLOBALIZATION\\SORTING\\'
          u'SORTDEFAULT.NLS',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\MSWSOCK.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\WSHQOS.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\WSHTCPIP.DLL',
          u'\\DEVICE\\HARDDISKVOLUME1\\WINDOWS\\SYSTEM32\\WSHIP6.DLL']

      self.assertEquals(strings_array, expected_strings_array)

  def testStringParsing(self):
    """Test parsing the ASCII string."""
    self.assertEquals(binary.ReadUtf16(self._ascii_string_1), 'Whatis')

    self.assertEquals(binary.ReadUtf16(self._ascii_string_2), 'What is this?')

    uni_text = binary.ReadUtf16(self._unicode_string_1)
    self.assertEquals(uni_text, u'þrándur')

  def testHex(self):
    """Test the hexadecimal representation of data."""
    hex_string_1 = binary.HexifyBuffer(self._ascii_string_1)
    hex_compare = (
        '\\x57\\x00\\x68\\x00\\x61\\x00\\x74\\x00\\x00\\x00\\x69\\x00'
        '\\x73\\x00')
    self.assertEquals(hex_string_1, hex_compare)

    hex_string_2 = binary.HexifyBuffer(self._unicode_string_1)
    hex_compare_unicode = (
        '\\xff\\xfe\\xfe\\x00\\x72\\x00\\xe1\\x00\\x6e\\x00\\x64\\x00'
        '\\x75\\x00\\x72\\x00')

    self.assertEquals(hex_string_2, hex_compare_unicode)


if __name__ == '__main__':
  unittest.main()
