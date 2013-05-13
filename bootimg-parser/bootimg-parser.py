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

Unpack boot.img:
python bootimg-parser.py -i boot.img

Pack boot image into boot.img:
python bootimg-parser.py -d bootimg-dir
'''

import os, sys
import getopt
import struct
import subprocess
from datetime import datetime

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

HEADER_SZ = 608
PAGE_SZ = 2048

ADDR_BASE   = 0x0
ADDR_OFFSET = 0x2000000
TAGS_ADDR   = 0x1e00000

'''
Class Definition
'''

'''
Class of Boot Image Header
'''
class Bi_Hdr(object):
    s = struct.Struct('8sIIIIIIIIII16s512s8I')

    def __init__(self, data):
        unpacked_data      = (Bi_Hdr.s).unpack(data)
        self.unpacked_data = unpacked_data

        self.magic          = unpacked_data[0]
        self.kernel_sz      = unpacked_data[1]
        self.kernel_addr    = unpacked_data[2]
        self.ramdisk_sz     = unpacked_data[3]
        self.ramdisk_addr   = unpacked_data[4]
        self.second_sz      = unpacked_data[5]
        self.second_addr    = unpacked_data[6]
        self.tags_addr      = unpacked_data[7]
        self.page_sz        = unpacked_data[8]
        self.dt_sz          = unpacked_data[9]
        self.unused         = unpacked_data[10]
        self.product_name   = unpacked_data[11]
        self.kernel_cmdline = unpacked_data[12]
        self.id             = unpacked_data[13]

    def __del__(self):
        pass

    def get_packed_data(self):
        values = [self.magic,
                  self.kernel_sz,
                  self.kernel_addr,
                  self.ramdisk_sz,
                  self.ramdisk_addr,
                  self.second_sz,
                  self.second_addr,
                  self.tags_addr,
                  self.page_sz,
                  self.dt_sz,
                  self.unused,
                  self.product_name,
                  self.kernel_cmdline,
                  self.id]

        return (Bi_Hdr.s).pack(*values)

    def show(self):
        print >> sys.stdout, 'Magic          : ' + self.magic
        print >> sys.stdout, 'Kernel Size    : ' + str(self.kernel_sz)
        print >> sys.stdout, 'Kernel Address : ' + str(hex(self.kernel_addr))
        print >> sys.stdout, 'Ramdisk Size   : ' + str(self.ramdisk_sz)
        print >> sys.stdout, 'Ramdisk Address: ' + str(hex(self.ramdisk_addr))
        print >> sys.stdout, 'Second Size    : ' + str(self.second_sz)
        print >> sys.stdout, 'Second Address : ' + str(hex(self.second_addr))
        print >> sys.stdout, 'Tags Address   : ' + str(hex(self.tags_addr))
        print >> sys.stdout, 'Page Size      : ' + str(self.page_sz)
        print >> sys.stdout, 'DT Size        : ' + str(self.dt_sz)
        print >> sys.stdout, 'Unused         : ' + str(self.unused)
        print >> sys.stdout, 'Product Name   : ' + str(self.product_name)
        print >> sys.stdout, 'Kernel Cmdline : ' + str(self.kernel_cmdline)
        print >> sys.stdout, 'ID             : ' + str(hex(self.id))

'''
Class of Unpacker
'''
class Unpacker(object):
    def __init__(self, fname):
        self.fname = ''
        self.fp = -1
        self.dirname = ''
        self.header = None
        self.dt = None

        self.buf_header   = None
        self.buf_kernel   = None
        self.buf_ramdisk  = None
        self.buf_secstage = None
        self.buf_dt       = None
        self.buf_sig      = None

        self.pg_header   = 0
        self.pg_kernel   = 0
        self.pg_ramdisk  = 0
        self.pg_secstage = 0
        self.pg_dt       = 0
        self.sz_sig      = 0

        self.initialize(fname)

    def __del__(self):
        if self.fp != -1:
            self.fp.close()

    def initialize(self, fname):
        try:
            self.fp = open(fname, 'rb')

            time = str(datetime.now()).replace(':', '-').replace(' ', '-').replace('.', '-')
            self.dirname = os.path.join(os.getcwd(), 'bootimg-' + time)
            os.makedirs(self.dirname)
        except IOError, err:
            if self.fp != -1:
                self.fp.close()
            raise os.error, err

        self.fname = fname

        try:
            self.populate_header()
            self.populate_kernel()
            self.populate_ramdisk()
            self.populate_secstage()
            self.populate_dt()
            self.populate_sig()
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
            self.header = Bi_Hdr(self.buf_header)
        except IOError, err:
            raise os.error, err

        if self.header.page_sz != PAGE_SZ:
            raise os.error, 'invalid page size!'

        self.header.show()
        print >> sys.stdout

        self.pg_header   = 1
        self.pg_kernel   = (self.header.kernel_sz + self.header.page_sz - 1) / self.header.page_sz
        self.pg_ramdisk  = (self.header.ramdisk_sz + self.header.page_sz - 1) / self.header.page_sz
        self.pg_secstage = (self.header.second_sz + self.header.page_sz - 1) / self.header.page_sz
        self.pg_dt       = (self.header.dt_sz + self.header.page_sz - 1) / self.header.page_sz

        try:
            fp_cmdline = open(os.path.join(self.dirname, 'cmdline'), 'ab')
            fp_cmdline.write(str(self.header.kernel_cmdline))
            fp_cmdline.close()
        except IOError, err:
            if fp_cmdline != -1:
                fp_cmdline.close()
            raise os.error, err

    def populate_kernel(self):
        if self.pg_kernel == 0:
            raise os.error, 'pages of kernel is 0.'

        try:
            offset = self.pg_header * self.header.page_sz
            self.fp.seek(offset, os.SEEK_SET)
            self.buf_kernel = self.fp.read(self.header.kernel_sz)

            fp_kernel = open(os.path.join(self.dirname, 'kernel'), 'ab')
            fp_kernel.write(str(self.buf_kernel))
            fp_kernel.close()
        except IOError, err:
            if fp_kernel != -1:
                fp_kernel.close()
            raise os.error, err

    def populate_ramdisk(self):
        if self.pg_ramdisk == 0:
            raise os.error, 'pages of ramdisk is 0.'

        try:
            offset = (self.pg_header + self.pg_kernel) * self.header.page_sz
            self.fp.seek(offset, os.SEEK_SET)
            self.buf_ramdisk = self.fp.read(self.header.ramdisk_sz)

            fp_ramdisk = open(os.path.join(self.dirname, 'ramdisk.cpio.gz'), 'ab')
            fp_ramdisk.write(str(self.buf_ramdisk))
            fp_ramdisk.close()

            os.makedirs(os.path.join(self.dirname, 'ramdisk'))
        except IOError, err:
            if fp_ramdisk != -1:
                fp_ramdisk.close()
            raise os.error, err

        os.chdir(os.path.join(self.dirname, 'ramdisk'))

        proc1 = subprocess.Popen(['gunzip', '-c', '../ramdisk.cpio.gz'], stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['cpio', '-i'], stdin=proc1.stdout, stdout=subprocess.PIPE)
        proc1.stdout.close()
        outs, errs = proc2.communicate()
        if proc2.returncode != 0:
            raise os.error, 'failed to unpack ramdisk!'

        os.chdir(self.dirname)
        try:
            os.remove(os.path.join(self.dirname, 'ramdisk.cpio.gz'))
        except IOError, err:
            raise os.error, err

    def populate_secstage(self):
        if self.pg_secstage == 0:
            return

        try:
            offset = (self.pg_header + self.pg_kernel + self.pg_ramdisk) * self.header.page_sz
            self.fp.seek(offset, os.SEEK_SET)
            self.buf_secstage = self.fp.read(self.header.second_sz)

            fp_secstage = open(os.path.join(self.dirname, 'secstage'), 'ab')
            fp_secstage.write(str(self.buf_secstage))
            fp_secstage.close()
        except IOError, err:
            if fp_secstage != -1:
                fp_secstage.close()
            raise os.error, err

    def populate_dt(self):
        if self.pg_dt == 0:
            return

        try:
            offset = (self.pg_header + self.pg_kernel + self.pg_ramdisk + self.pg_secstage) * self.header.page_sz
            self.fp.seek(offset, os.SEEK_SET)
            self.buf_dt = self.fp.read(self.header.dt_sz)

            fp_dt = open(os.path.join(self.dirname, 'dt.img'), 'ab')
            fp_dt.write(str(self.buf_dt))
            fp_dt.close()
        except IOError, err:
            if fp_dt != -1:
                fp_dt.close()
            raise os.error, err

    def populate_sig(self):
        try:
            offset = (self.pg_header + self.pg_kernel + self.pg_ramdisk + self.pg_secstage + self.pg_dt) * self.header.page_sz
            if offset == os.stat(self.fname).st_size:
                return
            self.fp.seek(offset, os.SEEK_SET)
            self.buf_sig = self.fp.read()

            fp_sig = open(os.path.join(self.dirname, 'signature'), 'ab')
            fp_sig.write(str(self.buf_sig))
            fp_sig.close()
        except IOError, err:
            if fp_sig != -1:
                fp_sig.close()
            raise os.error, err

'''
Function Definition
'''

'''
Unpack boot image
'''
def unpack_bootimg(fname):
    try:
        unpacker = Unpacker(fname)
    except OSError, err:
        print >> sys.stderr, str(err)
        return False

    return True

'''
Pack boot image
'''
def pack_bootimg(dname, fname):
    mkbootfs  = os.path.join(os.getcwd(), 'tools', 'mkbootfs')
    minigzip  = os.path.join(os.getcwd(), 'tools', 'minigzip')
    mkbootimg = os.path.join(os.getcwd(), 'tools', 'mkbootimg')

    kernel          = os.path.join(dname, 'kernel')
    ramdisk         = os.path.join(dname, 'ramdisk')
    ramdisk_cpio_gz = os.path.join(os.getcwd(), 'ramdisk.cpio.gz')

    '''
    Pack ramdisk.cpio.gz
    '''
    fp_ramdisk_cpio_gz = open(ramdisk_cpio_gz, 'ab')
    proc1 = subprocess.Popen([mkbootfs, ramdisk], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen([minigzip], stdin=proc1.stdout, stdout=fp_ramdisk_cpio_gz)
    proc1.stdout.close()
    outs, errs = proc2.communicate()
    if proc2.returncode != 0:
        print >> sys.stderr, 'failed to pack ramdisk!'
        return False

    '''
    Pack boot.img
    '''
    fp_cmdline = open(os.path.join(dname, 'cmdline'))
    cmdline = fp_cmdline.read().strip('\x00')
    fp_cmdline.close()

    cmd = mkbootimg \
        + ' --kernel ' + kernel \
        + ' --ramdisk ' + ramdisk_cpio_gz \
        + ' --base %x' % ADDR_BASE \
        + ' --pagesize %d' % PAGE_SZ \
        + ' --offset %x' % ADDR_OFFSET \
        + ' --cmdline ' + '\"' + cmdline + '\"' \
        + ' --output ' + fname
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    outs, errs = proc.communicate()
    if proc.returncode != 0:
        print >> sys.stderr, 'failed to pack boot image!'
        return False        

    os.remove(ramdisk_cpio_gz)

    '''
    Populate header of boot.img
    '''
    fp = -1
    try:
        fp = open(fname, 'r+b')
        offset = 0
        fp.seek(offset, os.SEEK_SET)
        buf_header = fp.read(HEADER_SZ)
        header = Bi_Hdr(buf_header)
    except IOError, err:
        if fp != -1:
            fp.close()
        print >> sys.stderr, str(err)
        return False

    if header.page_sz != PAGE_SZ:
        print >> sys.stderr, 'invalid page size!'
        return False

    pg_header   = 1
    pg_kernel   = (header.kernel_sz + header.page_sz - 1) / header.page_sz
    pg_ramdisk  = (header.ramdisk_sz + header.page_sz - 1) / header.page_sz
    pg_secstage = 0
    pg_dt       = 0
    sz_sig      = 0

    '''
    Append second stage to boot.img
    '''
    if os.access(os.path.join(dname, 'secstage'), os.F_OK | os.R_OK) is True:
        fp_secstage = -1
        try:
            fp_secstage = open(os.path.join(dname, 'secstage'), 'rb')
            buf_secstage = fp_secstage.read()
            header.second_sz = os.stat(os.path.join(dname, 'secstage')).st_size
            fp_secstage.close()

            offset = (pg_header + pg_kernel + pg_ramdisk) * header.page_sz
            fp.seek(offset, os.SEEK_SET)
            fp.write(buf_secstage)

            padding = header.page_sz - (header.second_sz % header.page_sz)
            if padding != header.page_sz:
                fp.write('\0' * padding)

            offset = 8 + 4 * 4
            fp.seek(offset, os.SEEK_SET)
            values = [header.second_sz]
            fp.write(struct.Struct('I').pack(*values))
        except IOError, err:
            if fp_secstage != -1:
                fp_secstage.close()
            if fp != -1:
                fp.close()
            print >> sys.stderr, str(err)
            return False

    '''
    Append device tree to boot.img
    '''
    if os.access(os.path.join(dname, 'dt.img'), os.F_OK | os.R_OK) is True:
        fp_dt = -1
        try:
            fp_dt = open(os.path.join(dname, 'dt.img'), 'rb')
            buf_dt = fp_dt.read()
            header.dt_sz = os.stat(os.path.join(dname, 'dt.img')).st_size
            fp_dt.close()

            offset = (pg_header + pg_kernel + pg_ramdisk + pg_secstage) * header.page_sz
            fp.seek(offset, os.SEEK_SET)
            fp.write(buf_dt)

            padding = header.page_sz - (header.dt_sz % header.page_sz)
            if padding != header.page_sz:
                fp.write('\0' * padding)

            offset = 8 + (4 * 8)
            fp.seek(offset, os.SEEK_SET)
            values = [header.dt_sz]
            fp.write(struct.Struct('I').pack(*values))
        except IOError, err:
            if fp_dt != -1:
                fp_dt.close()
            if fp != -1:
                fp.close()
            print >> sys.stderr, str(err)
            return False

    '''
    Append signature to boot.img
    '''
    '''Add code here'''

    '''
    Hack tags address
    '''
    offset = 8 + 4 * 6
    fp.seek(offset, os.SEEK_SET)
    values = [TAGS_ADDR]
    fp.write(struct.Struct('I').pack(*values))

    if fp != -1:
        fp.close()

    return True

'''
Print usage
'''
def print_usage():
    print >> sys.stdout, '\nUSAGE:\n'
    print >> sys.stdout, 'Unpack: python bootimg-parser.py -i boot.img'
    print >> sys.stdout, '  Pack: python bootimg-parser.py -d bootimg-dir\n'

'''
Main Entry
'''
def main():
    fname = ''
    dname = ''

    print >> sys.stdout, banner

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:h', ['image', 'dir', 'help'])
    except getopt.GetoptError, err:
        print >> sys.stderr, err
        print_usage()
        sys.exit(1)

    for o, a in opts:
        if o in ('-i', '--image'):
            fname = a
        elif o in ('-d', '--dir'):
            dname = a
        elif o in ('-h', '--help'):
            print_usage()
            sys.exit(0)
        else:
            continue

    if len(fname) != 0:
        if os.access(fname, os.F_OK | os.R_OK) is False:
            print >> sys.stderr, 'failed to access file!'
            sys.exit(1)

        print >> sys.stdout, 'Unpack boot.img...\n'

        ret = unpack_bootimg(os.path.join(os.getcwd(), fname))
        if ret is True:
            print >> sys.stdout, '\nDone!\n'
        else:
            print >> sys.stdout, '\nFailed!\n'
            sys.exit(1)
    elif len(dname) != 0:
        if os.access(dname, os.F_OK | os.R_OK) is False:
            print >> sys.stderr, 'failed to access directory!'
            sys.exit(1)

        print >> sys.stdout, 'Pack boot image...\n'

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

        ret = pack_bootimg(os.path.join(os.getcwd(), dname), fname)
        if ret is True:
            print >> sys.stdout, '\nDone!\n'
        else:
            print >> sys.stdout, '\nFailed!\n'
            sys.exit(1)
    else:
        print_usage()
        sys.exit(1)

'''
App Entry
'''
if __name__ == '__main__':
    main()
