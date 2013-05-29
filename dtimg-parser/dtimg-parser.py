#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

'''
Example:

Unpack dt.img:
python dtimg-parser.py -i dt.img
OR:
python dtimg-parser.py -i dt.img -t /path/to/dtc

Pack dt blob into dt.img:
python dtimg-parser.py -d dtimg-dir
OR:
python dtimg-parser.py -d dtimg-dir -t /path/to/dtc
'''

import os, sys
import getopt
import struct
import subprocess
from datetime import datetime
from stat import *

'''
Global Variable Definition
'''
banner = '''
  __      _                     _       
 / _|_ __(_) ___ __ _ _ __   __| | ___  
| |_| '__| |/ __/ _` | '_ \ / _` |/ _ \ 
|  _| |  | | (_| (_| | | | | (_| | (_) |
|_| |_|  |_|\___\__,_|_| |_|\__,_|\___/ 
'''

HEADER_SZ = 4 + (4 * 2)
DEVENTRY_SZ = 4 * 5

PAGE_SZ = 2048

'''
Class Definition
'''

'''
Class of header
'''
class Header(object):
    s = struct.Struct('4sII')

    def __init__(self, data):
        unpacked_data      = (Header.s).unpack(data)
        self.unpacked_data = unpacked_data

        self.magic   = unpacked_data[0]
        self.version = unpacked_data[1]
        self.num_dtb = unpacked_data[2]

    def __del__(self):
        pass

    def get_packed_data(self):
        values = [self.magic,
                  self.version,
                  self.num_dtb]

        return (Header.s).pack(*values)

    def show(self):
        print >> sys.stdout, 'Magic       : ' + self.magic
        print >> sys.stdout, 'Version     : ' + str(self.version)
        print >> sys.stdout, 'Num of DTBs : ' + str(self.num_dtb)

'''
Class of device entry
'''
class DevEntry(object):
    s = struct.Struct('IIIII')

    def __init__(self, data):
        unpacked_data      = (DevEntry.s).unpack(data)
        self.unpacked_data = unpacked_data

        self.chipset  = unpacked_data[0]
        self.platform = unpacked_data[1]
        self.rev_num  = unpacked_data[2]
        self.offset   = unpacked_data[3]
        self.size     = unpacked_data[4]

    def __del__(self):
        pass

    def get_packed_data(self):
        values = [self.chipset,
                  self.platform,
                  self.rev_num,
                  self.offset,
                  self.size]

        return (DevEntry.s).pack(*values)

    def show(self):
        print >> sys.stdout, 'Chipset         : ' + str(self.chipset)
        print >> sys.stdout, 'Platform        : ' + str(self.platform)
        print >> sys.stdout, 'Revision number : ' + str(self.rev_num)
        print >> sys.stdout, 'Offset          : ' + str(self.offset)
        print >> sys.stdout, 'Size            : ' + str(self.size)

'''
Class of Unpacker
'''
class Unpacker(object):
    def __init__(self, fname, tool=None):
        self.fp = -1
        self.dirname = ''
        self.header = None
        self.deventry = None

        self.buf_header   = None
        self.buf_deventry = None
        self.buf_dtb      = None

        if len(tool) != 0 and os.access(tool, os.F_OK | os.X_OK) is True:
            self.tool = tool
        else:
            self.tool = ''

        self.initialize(fname)

    def __del__(self):
        if self.fp != -1:
            self.fp.close()

    def initialize(self, fname):
        try:
            self.fp = open(fname, 'rb')

            time = str(datetime.now()).replace(':', '-').replace(' ', '-').replace('.', '-')
            self.dirname = os.path.join(os.getcwd(), 'dtimg-' + time)
            os.makedirs(self.dirname)
        except IOError, err:
            if self.fp != -1:
                self.fp.close()
            raise os.error, err

        try:
            self.populate_header()
            self.populate_dt()
        except OSError, err:
            os.remove(self.dirname)
            if self.fp != -1:
                self.fp.close()
            raise os.error, err

    def populate_header(self):
        try:
            offset = 0
            self.fp.seek(offset, os.SEEK_SET)
            self.buf_header = self.fp.read(HEADER_SZ)
            self.header = Header(self.buf_header)

            fp_header = -1
            fp_header = open(os.path.join(self.dirname, 'header'), 'ab')
            fp_header.write(str(self.buf_header))
            fp_header.close()
        except IOError, err:
            if fp_header != -1:
                fp_header.close()
            raise os.error, err

        self.header.show()
        print >> sys.stdout

    def populate_dt(self):
        offset = HEADER_SZ
        for index in range(self.header.num_dtb):
            '''
            Populate device entry
            '''
            self.fp.seek(offset, os.SEEK_SET)
            self.buf_deventry = self.fp.read(DEVENTRY_SZ)
            self.deventry = DevEntry(self.buf_deventry)

            fp_deventry = -1
            fp_deventry = open(os.path.join(self.dirname, str(index) + '.deventry'), 'ab')
            fp_deventry.write(str(self.buf_deventry))
            fp_deventry.close()

            '''
            Populate dt blob
            '''
            fp_dtb = -1
            try:
                self.fp.seek(self.deventry.offset, os.SEEK_SET)
                self.buf_dtb = self.fp.read(self.deventry.size)

                fp_dtb = open(os.path.join(self.dirname, str(index) + '.dtb'), 'ab')
                fp_dtb.write(str(self.buf_dtb))
                fp_dtb.close()
            except IOError, err:
                if fp_dtb != -1:
                    fp_dtb.close()
                raise os.error, err

            print >> sys.stdout, 'Index           : ' + str(index)
            self.deventry.show()
            print >> sys.stdout, 'File            : ' + str(index) + '.deventry'
            print >> sys.stdout, '                  ' + str(index) + '.dtb'
            if len(self.tool) != 0:
                print >> sys.stdout, '                  ' + str(index) + '.dts'

            '''
            Disassemble dt blob
            '''
            if len(self.tool) != 0:
                fname_dtb = os.path.join(self.dirname, str(index) + '.dtb')
                fname_dts = os.path.join(self.dirname, str(index) + '.dts')
                proc = subprocess.Popen([self.tool, '-p', '1024', '-I', 'dtb', '-O', 'dts', '-o', fname_dts, fname_dtb], stdout=subprocess.PIPE)
                outs, errs = proc.communicate()
                if proc.returncode != 0:
                    raise os.error, 'failed to run dt tool!'

            print >> sys.stdout

            offset += DEVENTRY_SZ

'''
Function Definition
'''

'''
Unpack device tree image
'''
def unpack_dtimg(fname, tool):
    try:
        unpacker = Unpacker(fname, tool)
    except OSError, err:
        print >> sys.stderr, str(err)
        return False

    return True

'''
Pack device tree image
'''
def pack_dtimg(dname, fname, tool):
    '''
    Pack header
    '''
    fp = -1
    fp_header = -1
    try:
        fp_header = open(os.path.join(dname, 'header'))
        buf_header = fp_header.read()
        fp_header.close()

        fp = open(fname, 'w+b')
        offset = 0
        fp.seek(offset, os.SEEK_SET)
        fp.write(str(buf_header))
    except IOError, err:
        if fp != -1:
            fp.close()
        if fp_header != -1:
            fp_header.close()
        print >> sys.stderr, str(err)
        return False

    header = Header(buf_header)

    '''
    Pack device entry
    '''
    deventry_list = []
    for dir, dirs, files in os.walk(dname):
        for f in files:
            try:
                if f.rfind('.deventry') != -1:
                    name = os.path.join(dir, f)
                    if S_ISREG(os.stat(name).st_mode):
                        deventry_list.append(name)
            except os.error:
                pass

    if len(deventry_list) == 0:
        if fp != -1:
            fp.close()
        print >> sys.stderr, 'no device entry exist!'
        return False

    deventry_list.sort(key=str.lower, reverse=False)

    if header.num_dtb != len(deventry_list):
        print >> sys.stdout, 'device entry number not match with number in header,'
        print >> sys.stdout, 'and the number in header will be updated.'
        header.num_dtb = len(deventry_list)

    offset = HEADER_SZ
    for item in deventry_list:
        try:
            fp_deventry = -1
            fp_deventry = open(item)
            buf_deventry = fp_deventry.read()
            fp_deventry.close()

            fp.seek(offset, os.SEEK_SET)
            fp.write(str(buf_deventry))
        except IOError, err:
            if fp != -1:
                fp.close()
            if fp_deventry != -1:
                fp_deventry.close()
            print >> sys.stderr, str(err)
            return False

        offset += DEVENTRY_SZ

    padding = PAGE_SZ - ((header.num_dtb * DEVENTRY_SZ) % PAGE_SZ)
    if padding < 0:
        if fp != -1:
            fp.close()
        print >> sys.stderr, 'invalid padding!'
        return False
    if padding != PAGE_SZ:
        fp.write('\0' * padding)

    '''
    Pack dt blob
    '''
    '''
    Build dt blob from dt blob source using dt tool
    '''
    if len(tool) != 0 and os.access(tool, os.F_OK | os.X_OK) is True:
        dts_list = []
        for dir, dirs, files in os.walk(dname):
            for f in files:
                try:
                    if f.rfind('.dts') != -1:
                        name = os.path.join(dir, f)
                        if S_ISREG(os.stat(name).st_mode):
                            dts_list.append(name)
                except os.error:
                    pass

        if len(dts_list) == header.num_dtb:
            dts_list.sort(key=str.lower, reverse=False)
            for f in dts_list:
                fname_dts = os.path.join(dname, f)
                fname_dtb = os.path.join(dname, f.replace('.dts', '.dtb'))
                proc = subprocess.Popen([tool, '-p', '1024', '-I', 'dts', '-O', 'dtb', '-o', fname_dtb, fname_dts], stdout=subprocess.PIPE)
                outs, errs = proc.communicate()
                if proc.returncode != 0:
                    print >> sys.stderr, 'failed to run dt tool!'
                    return False
        elif len(dts_list) == 0:
            pass
        else:
            if fp != -1:
                fp.close()
            print >> sys.stderr, 'invalid device tree blob source number!'
            return False

    '''
    Walk directory for dt blob
    '''
    dtb_list = []
    for dir, dirs, files in os.walk(dname):
        for f in files:
            try:
                if f.rfind('.dtb') != -1:
                    name = os.path.join(dir, f)
                    if S_ISREG(os.stat(name).st_mode):
                        dtb_list.append(name)
            except os.error:
                pass

    if len(dtb_list) == 0:
        if fp != -1:
            fp.close()
        print >> sys.stderr, 'no device tree blob exist!'
        return False

    dtb_list.sort(key=str.lower, reverse=False)

    if header.num_dtb != len(dtb_list):
        if fp != -1:
            fp.close()
        print >> sys.stderr, 'invalid device tree blob number!'
        return False

    header_deventry_size = HEADER_SZ + (header.num_dtb * DEVENTRY_SZ)
    padding = PAGE_SZ - (header_deventry_size % PAGE_SZ)
    if padding == PAGE_SZ:
        padding = 0
    offset_dtb = header_deventry_size + padding
    for index in range(header.num_dtb):
        try:
            fp_deventry = -1
            fp_deventry = open(deventry_list[index])
            buf_deventry = fp_deventry.read()
            deventry = DevEntry(buf_deventry)
            fp_deventry.close()

            fp_dtb = -1
            fp_dtb = open(dtb_list[index])
            buf_dtb = fp_dtb.read()
            fp_dtb.close()

            deventry.offset = offset_dtb
            padding = PAGE_SZ - ((deventry.offset + os.stat(dtb_list[index]).st_size) % PAGE_SZ)
            if padding == PAGE_SZ:
                padding = 0
            deventry.size = os.stat(dtb_list[index]).st_size + padding

            '''
            Update dt blob data
            '''
            offset = deventry.offset
            fp.seek(offset, os.SEEK_SET)
            fp.write(str(buf_dtb))
            fp.write('\0' * padding)

            '''
            Update dt blob offset/size in device entry
            '''
            offset = HEADER_SZ + (index * DEVENTRY_SZ)
            fp.seek(offset, os.SEEK_SET)
            fp.write(str(deventry.get_packed_data()))

            offset_dtb = deventry.offset + deventry.size
        except IOError, err:
            if fp != -1:
                fp.close()
            if fp_deventry != -1:
                fp_deventry.close()
            if fp_dtb != -1:
                fp_dtb.close()
            print >> sys.stderr, str(err)
            return False

    '''
    Update header
    '''
    offset = 0
    fp.seek(offset, os.SEEK_SET)
    fp.write(str(header.get_packed_data()))

    if fp != -1:
        fp.close()

    return True

'''
Print usage
'''
def print_usage():
    print >> sys.stdout, '\nUSAGE:\n'
    print >> sys.stdout, 'Unpack: python dtimg-parser.py -i dt.img'
    print >> sys.stdout, '        OR:'
    print >> sys.stdout, '        python dtimg-parser.py -i dt.img -t /path/to/dtc\n'
    print >> sys.stdout, '  Pack: python dtimg-parser.py -d dtimg-dir'
    print >> sys.stdout, '        OR:'
    print >> sys.stdout, '        python dtimg-parser.py -d dtimg-dir -t /path/to/dtc\n'

'''
Main Entry
'''
def main():
    fname = ''
    dname = ''
    tool = ''

    print >> sys.stdout, banner

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:t:h', ['image', 'dir', 'tool', 'help'])
    except getopt.GetoptError, err:
        print >> sys.stderr, err
        print_usage()
        sys.exit(1)

    for o, a in opts:
        if o in ('-i', '--image'):
            fname = a
        elif o in ('-d', '--dir'):
            dname = a
        elif o in ('-t', '--tool'):
            tool = a
        elif o in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        else:
            continue

    if len(fname) != 0:
        if os.access(fname, os.F_OK | os.R_OK) is False:
            print >> sys.stderr, 'failed to access file!'
            sys.exit(1)

        print >> sys.stdout, 'Unpack dt.img...\n'

        ret = unpack_dtimg(os.path.join(os.getcwd(), fname), tool)
        if ret is True:
            print >> sys.stdout, '\nDone!\n'
        else:
            print >> sys.stdout, '\nFailed!\n'
            sys.exit(1)
    elif len(dname) != 0:
        if os.access(dname, os.F_OK | os.R_OK) is False:
            print >> sys.stderr, 'failed to access directory!'
            sys.exit(1)

        print >> sys.stdout, 'Pack dt image...\n'

        if dname[-1] == '/':
            index = dname.rfind('/', 0, len(dname)-1)
            if index != -1:
                fname = os.path.join(os.getcwd(), dname[index+1:len(dname)-1] + '.img')
            else:
                fname = os.path.join(os.getcwd(), dname[:len(dname)-1] + '.img')
        else:
            index = dname.rfind('/', 0, len(dname))
            if index != -1:
                fname = os.path.join(os.getcwd(), dname[index+1:] + '.img')
            else:
                fname = os.path.join(os.getcwd(), dname + '.img')

        ret = pack_dtimg(os.path.join(os.getcwd(), dname), fname, tool)
        if ret is True:
            print >> sys.stdout, '\nDone!\n'
        else:
            print >> sys.stdout, '\nFailed!\n'
            if os.access(fname, os.F_OK) is True:
                os.remove(fname)
            sys.exit(1)
    else:
        print_usage()
        sys.exit(1)

'''
App Entry
'''
if __name__ == '__main__':
    main()
