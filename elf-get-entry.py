#!/usr/bin/env python

# Copyright (c) 2015, NVIDIA CORPORATION.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# elf-get-entry.py: Print the entry point of an ELF binary

import sys
import struct

if len(sys.argv) != 2:
    print >>sys.stderr, "usage: %s filename.elf" % sys.argv[0]
    sys.exit(-1)

f = file(sys.argv[1], 'rb')
data = f.read(0x20)
f.close()

if data[0:4] != '\x7fELF':
    print >>sys.stderr, "ELF magic mismatch"
    sys.exit(-1)

ei_class = ord(data[4])
if ei_class == 1:
    elf_bytes = 4
    struct_type = 'I'
elif ei_class == 2:
    elf_bytes = 8
    struct_type = 'Q'
else:
    print >>sys.stderr, "Bad EI_CLASS value"
    sys.exit(-1)

ei_data = ord(data[5])
if ei_data == 1:
    struct_endian = '<'
elif ei_data == 2:
    struct_endian = '>'
else:
    print >>sys.stderr, "Bad EI_DATA value"
    sys.exit(-1)

ei_version = ord(data[6])
if ei_version != 1:
    print >>sys.stderr, "Bad EI_VERSION value"
    sys.exit(-1)

e_entry = data[0x18:0x18 + elf_bytes]
ep = struct.unpack(struct_endian + struct_type, e_entry)
print '0x%x' % ep
