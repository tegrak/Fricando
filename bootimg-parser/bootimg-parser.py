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
#
# Example:
#
# To unpack boot.img:
# $ bootimg-parser.py boot.img
#
# To pack dir into boot.img:
# $ bootimg-parser.py bootimg-dir
#

import os, sys
from datetime import datetime

#
# Global Variable Definition
#
banner = '''
  __      _                     _       
 / _|_ __(_) ___ __ _ _ __   __| | ___  
| |_| '__| |/ __/ _` | '_ \ / _` |/ _ \ 
|  _| |  | | (_| (_| | | | | (_| | (_) |
|_| |_|  |_|\___\__,_|_| |_|\__,_|\___/ 
'''

addr_base = 0x80200000
addr_offset = 0x02000000

#
# Class Definition For Unpacker
#
class Unpacker(object):
    def __init__(self, img):
        #
        # Init class member
        #
        self.image = img

        self.sec_pg_header = 0
        self.sec_pg_kernel = 0
        self.sec_pg_ramdisk = 0
        self.sec_pg_second= 0
        self.sec_pg_dt = 0
        self.sec_sz_sig = 0

        self.hdr_magic = "ANDROID!"
        self.hdr_kernel_sz = 0
        self.hdr_kernel_addr = 0x0
        self.hdr_ramdisk_sz = 0
        self.hdr_ramdisk_addr = 0x0
        self.hdr_second_sz = 0
        self.hdr_second_addr = 0x0
        self.hdr_tags_addr = 0x0
        self.hdr_page_sz = 0
        self.hdr_dt_sz = 0
        self.hdr_unused = 0
        self.hdr_name = None
        self.hdr_cmdline = None
        self.hdr_id = None

    #
    # Convert string to integer
    #
    def str2int(self, str_list):
        i = 0
        data = 0
        str_len = len(str_list)

        while (i < str_len):
            data += ord(str_list[i]) << (i * 8)
            i += 1

        return data

    #
    # Check magic
    #
    def check_magic(self):
        magic = self.image[0:len(self.hdr_magic[:-1])]
        
        if magic == self.hdr_magic[:-1]:
            return True
        else:
            return False

    #
    # Parse header
    #
    def parse_header(self):
        offset = len(self.hdr_magic[:-1]) + 1
        self.hdr_kernel_sz = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_kernel_addr = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_ramdisk_sz = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_ramdisk_addr = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_second_sz = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_second_addr = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_tags_addr = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_page_sz = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_dt_sz = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_unused = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_name = self.image[offset:offset+16]

        offset += 16
        self.hdr_cmdline = self.image[offset:offset+512]

        offset += 512
        self.hdr_id = self.str2int(self.image[offset:offset+8*4])

    #
    # Calculate page size
    #
    def calc_page_sz(self):
        self.sec_pg_header = 1
        self.sec_pg_kernel = (self.hdr_kernel_sz + self.hdr_page_sz - 1) / self.hdr_page_sz
        self.sec_pg_ramdisk = (self.hdr_ramdisk_sz + self.hdr_page_sz - 1) / self.hdr_page_sz
        self.sec_pg_second = (self.hdr_second_sz + self.hdr_page_sz - 1) / self.hdr_page_sz
        self.sec_pg_dt = (self.hdr_dt_sz + self.hdr_page_sz - 1) / self.hdr_page_sz

    #
    # Unpack kernel
    #
    def unpack_kernel(self, dir_unpacked):
        if (self.sec_pg_kernel is 0):
            return

        fp = open(os.path.join(dir_unpacked, "kernel"), "ab")
        fp.write(self.image[self.sec_pg_header*self.hdr_page_sz:self.sec_pg_header*self.hdr_page_sz+self.sec_pg_kernel*self.hdr_page_sz])
        fp.close()

    #
    # Unpack ramdisk
    #
    def unpack_ramdisk(self, dir_unpacked):
        if (self.sec_pg_ramdisk is 0):
            return

        fp = open(os.path.join(dir_unpacked, "ramdisk.cpio.gz"), "ab")
        fp.write(self.image[(self.sec_pg_header+self.sec_pg_kernel)*self.hdr_page_sz:(self.sec_pg_header+self.sec_pg_kernel)*self.hdr_page_sz+self.sec_pg_ramdisk*self.hdr_page_sz])
        fp.close()

        os.chdir(os.path.join(dir_unpacked, "ramdisk"))
        os.system("gunzip -c ../ramdisk.cpio.gz | cpio -i")
        os.chdir(dir_unpacked)

        os.remove(os.path.join(dir_unpacked, "ramdisk.cpio.gz"))

    #
    # Unpack second stage
    #
    def unpack_second(self, dir_unpacked):
        if (self.sec_pg_second is 0):
            return

        fp = open(os.path.join(dir_unpacked, "secondstage.img"), "ab")
        fp.write(self.image[(self.sec_pg_header+self.sec_pg_kernel+self.sec_pg_ramdisk)*self.hdr_page_sz:(self.sec_pg_header+self.sec_pg_kernel+self.sec_pg_ramdisk)*self.hdr_page_sz+self.sec_pg_second*self.hdr_page_sz])
        fp.close()

    #
    # Unpack device tree
    #
    def unpack_dt(self, dir_unpacked):
        if (self.sec_pg_dt is 0):
            return

        fp = open(os.path.join(dir_unpacked, "devicetree.img"), "ab")
        fp.write(self.image[(self.sec_pg_header+self.sec_pg_kernel+self.sec_pg_ramdisk+self.sec_pg_second)*self.hdr_page_sz:(self.sec_pg_header+self.sec_pg_kernel+self.sec_pg_ramdisk+self.sec_pg_second)*self.hdr_page_sz+self.sec_pg_dt*self.hdr_page_sz])
        fp.close()

    #
    # Unpack signiture pad
    #
    def unpack_sig(self, dir_unpacked):
        sig_pad_sz = len(self.image) - ((self.sec_pg_header + self.sec_pg_kernel + self.sec_pg_ramdisk + self.sec_pg_second + self.sec_pg_dt) * self.hdr_page_sz)

        if (sig_pad_sz is 0):
            return

        self.sec_sz_sig = sig_pad_sz

        fp = open(os.path.join(dir_unpacked, "signiture.pad"), "ab")
        fp.write(self.image[(self.sec_pg_header+self.sec_pg_kernel+self.sec_pg_ramdisk+self.sec_pg_second+self.sec_pg_dt)*self.hdr_page_sz:(self.sec_pg_header+self.sec_pg_kernel+self.sec_pg_ramdisk+self.sec_pg_second+self.sec_pg_dt)*self.hdr_page_sz+self.sec_sz_sig])
        fp.close()

    #
    # Get address base
    #
    def get_page_sz(self):
        return self.hdr_page_sz;

    #
    # Get cmdline
    #
    def get_cmdline(self):
        return self.hdr_cmdline;

    #
    # Print header info
    #
    def print_header_info(self):
        print("          Magic: " + self.hdr_magic)

        print("    Kernel Size: " + str(self.hdr_kernel_sz) + " (" + str(self.sec_pg_kernel*self.hdr_page_sz) + " padded)")
        print(" Kernel Address: " + str(hex(self.hdr_kernel_addr)))

        print("   Ramdisk Size: " + str(self.hdr_ramdisk_sz) + " (" + str(self.sec_pg_ramdisk*self.hdr_page_sz) + " padded)")
        print("Ramdisk Address: " + str(hex(self.hdr_ramdisk_addr)))

        print("    Second Size: " + str(self.hdr_second_sz) + " (" + str(self.sec_pg_second*self.hdr_page_sz) + " padded)")
        print(" Second Address: " + str(hex(self.hdr_second_addr)))

        print("   Tags Address: " + str(hex(self.hdr_tags_addr)))
        print("      Page Size: " + str(self.hdr_page_sz))
        print("        DT Size: " + str(self.hdr_dt_sz) + " (" + str(self.sec_pg_dt*self.hdr_page_sz) + " padded)")
        print("         Unused: " + str(self.hdr_unused))
        print("           Name: " + str(self.hdr_name))

        print("   Command Line: " + str(self.hdr_cmdline))

        print("             ID: " + str(hex(self.hdr_id)))

        print("")

    #
    # Print signiture pad info
    #
    def print_sig_pad_info(self):
        if self.sec_sz_sig is 0:
            return
        print("   Sig Pad Size: " + str(self.sec_sz_sig))

    #
    # Run routine
    #
    def run(self):
        now = datetime.now()
        time = str(now).replace(":", "-").replace(" ", "-").replace(".", "-")
        dir_unpacked = os.path.join(os.getcwd(), "bootimg-" + time)

        #
        # Create dir for unpacking image
        #
        try:
            os.makedirs(os.path.join(dir_unpacked, "ramdisk"))
        except OSError:
            print("\nERROR: dir existed!\n")
            return

        #
        # Check magic
        #
        if self.check_magic() is False:
            print("\nERROR: invalid magic!\n")
            return

        #
        # Parse header
        #
        self.parse_header()

        #
        # Calculate page size
        #
        self.calc_page_sz()

        #
        # Print header info
        #
        self.print_header_info()

        #
        # Print signiture pad info
        #
        self.print_sig_pad_info()

        #
        # Unpack kernel
        #
        self.unpack_kernel(dir_unpacked)

        #
        # Unpack ramdisk
        #
        self.unpack_ramdisk(dir_unpacked)

        #
        # Unpack second stage
        #
        self.unpack_second(dir_unpacked)

        #
        # Unpack device tree
        #
        self.unpack_dt(dir_unpacked)

        #
        # Unpack signiture pad
        #
        self.unpack_sig(dir_unpacked)

#
# Function Definition
#

#
# Unpack boot image
#
def unpack_bootimg(image_file):
    fp = open(image_file, "rb")

    image_data = fp.read()
    unpacker = Unpacker(image_data)
    unpacker.run()

    fp.close()

    ''' test only
    print(hex(ord(image_data[0])))
    data_hex = binascii.b2a_hex(image_data[1])
    print(data_hex[0:4][::-1])
    '''

    return True

#
# Packed into boot image
#
def pack_bootimg(image_dir, image_file):
    mkbootfs  = os.path.join(os.getcwd(), "tools", "mkbootfs")
    minigzip  = os.path.join(os.getcwd(), "tools", "minigzip")
    mkbootimg = os.path.join(os.getcwd(), "tools", "mkbootimg")
    kernel = os.path.join(image_dir, "kernel")
    ramdisk_dir = os.path.join(image_dir, "ramdisk")
    ramdisk     = os.path.join(os.getcwd(), "ramdisk.cpio.gz")

    fp = open(image_file, "rb")
    image_data = fp.read()
    unpacker = Unpacker(image_data)
    fp.close()

    if unpacker.check_magic() is False:
        print("\nERROR: invalid magic!\n")
        return False

    unpacker.parse_header()
    page_sz = unpacker.get_page_sz()
    cmdline = unpacker.get_cmdline().strip("\x00")

    os.system(mkbootfs + " " + ramdisk_dir
              + "|"
              + minigzip + ">" + ramdisk)

    os.system(mkbootimg
              + " --kernel " + kernel
              + " --ramdisk " + ramdisk
              + " --base %x" % addr_base
              + " --pagesize %d" % page_sz
              + " --offset %x" % addr_offset
              + " --cmdline " + "\"" + cmdline + "\""
              + " --output " + image_file)

    os.remove(ramdisk)

    return True

#
# Print usage
#
def print_usage():
    print("USAGE:\n")
    print("1. Unpack 'boot.img': ./bootimg-parser.py boot.img\n")
    print("2. Packed into 'boot.img': ./bootimg-parser.py bootimg-dir\n")

#
# Main Entry
#
def main():
    #
    # Display banner
    #
    print(banner)

    #
    # Get args list
    #
    args = sys.argv
    args_len = len(args)

    #
    # Check args input
    #
    if args_len is 2:
        if args[1] == "boot.img" and os.path.isfile(os.path.join(os.getcwd(), args[1])) is True:
            print("\nUnpacking boot.img...\n")
            ret = unpack_bootimg(os.path.join(os.getcwd(), args[1]))
            if ret is True:
                print("\nDone!\n")
            else:
                print("\nFailed!\n")

        elif os.path.isdir(os.path.join(os.getcwd(), args[1])) is True and os.path.isfile(os.path.join(os.getcwd(), "boot.img")) is True:
            print("\nPacking files for boot.img...\n")
            ret = pack_bootimg(os.path.join(os.getcwd(), args[1]), os.path.join(os.getcwd(), "boot.img"))
            if ret is True:
                print("Done!\n")
            else:
                print("Failed!\n")

        else:
            print("\nERROR: invalid parameter!\n")
            print_usage()

    else:
        print("\nERROR: invalid parameter!\n")
        print_usage()

#
# App Entry
#
if __name__ == '__main__':
    main()
