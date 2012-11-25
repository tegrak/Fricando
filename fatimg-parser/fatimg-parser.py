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
# To parse FAT image:
# python fatimg-parser.py fat.img
#

import os, sys
import getopt
import copy

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

#
# Global Variables Definition
#

#
# FAT Parameters
#
FAT_SECTOR_SZ = 512
FAT_DIR_ENT_LEN = 32

#
# FAT16 Parameters
#
FAT16_ENTRY_SZ = 2

FAT16_ROOTDIR_ENT_MAX = 512

FAT16_CLUSTER_SZ  = (16 * 1024)
FAT16_CLUSTER_NUM = (64 * 1024 * 1024) / FAT16_CLUSTER_SZ

FAT16_SECTOR_NUM = (64 * 1024 * 1024) / FAT_SECTOR_SZ

#
# Class Definition For Parser
#
class FATParser(object):
    def __init__(self, img):
        #
        # Init class member
        #
        self.image = img

        #
        # FAT common header
        #
        self.fat_common_hdr_jumpcode = []
        self.fat_common_hdr_oem_name = ""
        self.fat_common_hdr_bytespersec = 0
        self.fat_common_hdr_secpercluster = 0
        self.fat_common_hdr_secreserved = 0
        self.fat_common_hdr_fatcopy_num = 0
        self.fat_common_hdr_rootdirent_max = 0
        self.fat_common_hdr_small32mbsec_num = 0
        self.fat_common_hdr_mediadesc = 0
        self.fat_common_hdr_secperfat = 0
        self.fat_common_hdr_secpertrack = 0
        self.fat_common_hdr_heads_num = 0
        self.fat_common_hdr_hiddensec_num = 0
        self.fat_common_hdr_sec_num = 0

        #
        # FAT common header offset
        #
        self.offset_fat_common_hdr = 0

        #
        # FAT16 header
        #
        self.fat16_hdr_logicaldrive_num = 0
        #self.fat16_hdr_reserved = 0
        self.fat16_hdr_ext_sign = 0
        self.fat16_hdr_ser_num = 0
        self.fat16_hdr_vol_name = ""
        self.fat16_hdr_fat_name = ""
        self.fat16_hdr_exec_code = []
        self.fat16_hdr_exec_marker = []

        #
        # FAT16 header offset
        #
        self.offset_fat16_hdr = 0

        #
        # FAT directory entry list
        #
        #
        # FAT directory entry
        #
        self.fat_dirent = {
            'file_name': "",
            'file_ext': "",
            'file_attr': 0,
            'user_attr': 0,
            'file_timeresolution': 0,
            'file_timecreated': 0,
            'file_datecreated': 0,
            'file_datelastaccessed': 0,
            'file_accessrightmap': 0,
            'file_timelastmodified': 0,
            'file_datelastmodified': 0,
            'file_firstcluster': 0,
            'file_bytesize': 0
            }

        ''' test only
        self.fat16_table_sz = FAT16_CLUSTER_NUM * FAT16_ENTRY_SZ
        self.fat16_table_sz += (FAT_SECTOR_SZ - (self.fat_table_size % FAT_SECTOR_SZ))

        self.fat_common_hdr_format = struct.Struct('<3s8sHBHBHHBHHHII')
        self.fat_common_hdr_list = [
            '\xEB\x3C\x90',                    # jump_code_nop
            "MSDOS5.0"+(" "*(11-len("MSDOS5.0"))),
                                               # oem_name
            FAT_SECTOR_SZ,                     # bytes_per_sec
            FAT16_CLUSTER_SZ/FAT_SECTOR_SZ,    # sec_per_cluster
            1,                                 # reserved_sec
            2,                                 # num_fat_copies
            FAT16_ROOTDIR_ENT_MAX,             # max_root_dir_ent
            0,                                 # num_sec_small_32mb
            0xF8,                              # media_desc
            self.fat16_table_sz/FAT_SECTOR_SZ, # sec_per_fat
            63,                                # sec_per_track
            255,                               # num_heads
            0,                                 # num_hidden_sec
            FAT16_SECTOR_NUM                   # num_sec
            ]

        self.fat16_hdr_format = struct.Struct('<HBI11s8s448s2s')
        self.fat16_hdr_list = [
            0x80,                                # logical_drive_num
            #0,                                  # reserved
            0x29,                                # ext_sign
            12345678,                            # ser_num
            "NO NAME"+(" "*(11-len("NO NAME"))), # vol_name
            "FAT16"+(" "*(8-len("FAT16"))),      # fat_name
            '\x33\xC9\x8E\xD1\xBC\xF0\x7B\x8E\xD9\xB8\x00\x20\x8E\xC0\xFC\xBD\x00\x7C\x38\x4E\x24\x7D\x24\x8B\xC1\x99\xE8\x3C\x01\x72\x1C\x83\xEB\x3A\x66\xA1\x1C\x7C\x26\x66\x3B\x07\x26\x8A\x57\xFC\x75\x06\x80\xCA\x02\x88\x56\x02\x80\xC3\x10\x73\xEB\x33\xC9\x8A\x46\x10\x98\xF7\x66\x16\x03\x46\x1C\x13\x56\x1E\x03\x46\x0E\x13\xD1\x8B\x76\x11\x60\x89\x46\xFC\x89\x56\xFE\xB8\x20\x00\xF7\xE6\x8B\x5E\x0B\x03\xC3\x48\xF7\xF3\x01\x46\xFC\x11\x4E\xFE\x61\xBF\x00\x00\xE8\xE6\x00\x72\x39\x26\x38\x2D\x74\x17\x60\xB1\x0B\xBE\xA1\x7D\xF3\xA6\x61\x74\x32\x4E\x74\x09\x83\xC7\x20\x3B\xFB\x72\xE6\xEB\xDC\xA0\xFB\x7D\xB4\x7D\x8B\xF0\xAC\x98\x40\x74\x0C\x48\x74\x13\xB4\x0E\xBB\x07\x00\xCD\x10\xEB\xEF\xA0\xFD\x7D\xEB\xE6\xA0\xFC\x7D\xEB\xE1\xCD\x16\xCD\x19\x26\x8B\x55\x1A\x52\xB0\x01\xBB\x00\x00\xE8\x3B\x00\x72\xE8\x5B\x8A\x56\x24\xBE\x0B\x7C\x8B\xFC\xC7\x46\xF0\x3D\x7D\xC7\x46\xF4\x29\x7D\x8C\xD9\x89\x4E\xF2\x89\x4E\xF6\xC6\x06\x96\x7D\xCB\xEA\x03\x00\x00\x20\x0F\xB6\xC8\x66\x8B\x46\xF8\x66\x03\x46\x1C\x66\x8B\xD0\x66\xC1\xEA\x10\xEB\x5E\x0F\xB6\xC8\x4A\x4A\x8A\x46\x0D\x32\xE4\xF7\xE2\x03\x46\xFC\x13\x56\xFE\xEB\x4A\x52\x50\x06\x53\x6A\x01\x6A\x10\x91\x8B\x46\x18\x96\x92\x33\xD2\xF7\xF6\x91\xF7\xF6\x42\x87\xCA\xF7\x76\x1A\x8A\xF2\x8A\xE8\xC0\xCC\x02\x0A\xCC\xB8\x01\x02\x80\x7E\x02\x0E\x75\x04\xB4\x42\x8B\xF4\x8A\x56\x24\xCD\x13\x61\x61\x72\x0B\x40\x75\x01\x42\x03\x5E\x0B\x49\x75\x06\xF8\xC3\x41\xBB\x00\x00\x60\x66\x6A\x00\xEB\xB0\x42\x4F\x4F\x54\x4D\x47\x52\x20\x20\x20\x20\x0D\x0A\x52\x65\x6D\x6F\x76\x65\x20\x64\x69\x73\x6B\x73\x20\x6F\x72\x20\x6F\x74\x68\x65\x72\x20\x6D\x65\x64\x69\x61\x2E\xFF\x0D\x0A\x44\x69\x73\x6B\x20\x65\x72\x72\x6F\x72\xFF\x0D\x0A\x50\x72\x65\x73\x73\x20\x61\x6E\x79\x20\x6B\x65\x79\x20\x74\x6F\x20\x72\x65\x73\x74\x61\x72\x74\x0D\x0A\x00\x00\x00\x00\x00\x00\x00\xAC\xCB\xD8',
                                                 # exec_code
            '\x55\xAA',                          # exec_marker
            ]

        self.fat16_eoc = '\xF8\xFF\xFF\xFF' # last cluster in file (EOC)
        '''

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
    # Find FAT directory entry
    #
    def find_fat_dir_entry_helper(self, dir_cluster_data):
        for i in range(0, len(dir_cluster_data), FAT_DIR_ENT_LEN):
            dirent = dir_cluster_data[i:i+FAT_DIR_ENT_LEN]

            offset = 0
            self.fat_dirent['file_name'] = dirent[offset:offset+8]

            offset += 8
            self.fat_dirent['file_ext'] = dirent[offset:offset+3]

            offset += 3
            self.fat_dirent['file_attr'] = self.str2int(dirent[offset:offset+1])

            offset += 1
            self.fat_dirent['user_attr'] = self.str2int(dirent[offset:offset+1])

            offset += 1
            self.fat_dirent['file_timeresolution'] = self.str2int(dirent[offset:offset+1])

            offset += 1
            self.fat_dirent['file_timecreated'] = self.str2int(dirent[offset:offset+2])

            offset += 2
            self.fat_dirent['file_datecreated'] = self.str2int(dirent[offset:offset+2])

            offset += 2
            self.fat_dirent['file_datelastaccessed'] = self.str2int(dirent[offset:offset+2])

            offset += 2
            self.fat_dirent['file_accessrightmap'] = self.str2int(dirent[offset:offset+2])

            offset += 2
            self.fat_dirent['file_timelastmodified'] = self.str2int(dirent[offset:offset+2])

            offset += 2
            self.fat_dirent['file_datelastmodified'] = self.str2int(dirent[offset:offset+2])

            offset += 2
            self.fat_dirent['file_firstcluster'] = self.str2int(dirent[offset:offset+2])

            offset += 2
            self.fat_dirent['file_bytesize'] = self.str2int(dirent[offset:offset+4])

            if self.fat_dirent['file_attr'] != 0:
                self.print_fat_dir_entry(self.fat_dirent)

    #
    # Find FAT16 directory entry
    #
    def find_fat16_dir_entry(self, dir_table_start, dir_table_len):
        dir_cluster_data = self.image[dir_table_start:dir_table_start+dir_table_len]

        self.find_fat_dir_entry_helper(dir_cluster_data)

    #
    # Check FAT image ID
    #
    def check_fatimage_id(self):
        pass

    #
    # Parse FAT common header
    #
    def parse_fat_common_header(self):
        offset = self.offset_fat_common_hdr
        self.fat_common_hdr_jumpcode = self.str2int(self.image[offset:offset+3])

        offset += 3
        self.fat_common_hdr_oem_name = self.image[offset:offset+8]

        offset += 8
        self.fat_common_hdr_bytespersec = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.fat_common_hdr_secpercluster = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.fat_common_hdr_secreserved = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.fat_common_hdr_fatcopy_num = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.fat_common_hdr_rootdirent_max = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.fat_common_hdr_small32mbsec_num = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.fat_common_hdr_mediadesc = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.fat_common_hdr_secperfat = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.fat_common_hdr_secpertrack = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.fat_common_hdr_heads_num = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.fat_common_hdr_hiddensec_num = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.fat_common_hdr_sec_num = self.str2int(self.image[offset:offset+4])

        self.offset_fat16_hdr = offset + 4

        ''' test only
        fp.write(self.fat_common_hdr_format.pack(*self.fat_common_hdr_list))
        fp.write(self.fat16_hdr_format.pack(*self.fat16_hdr_list))
        fp.close()

        data = fp.read(fat_common_header.size)
        fat_data = fp.read(SECTOR_SIZE-fat_common_header.size)
        fp.close()
        all_bytes = self.fat_common_hdr_format.unpack(data)
        fat_common_hdr_list['jump_code_nop'] = all_bytes[0]
        all_bytes = self.fat16_hdr_format.unpack(fat_data)
        fat16_hdr_list['logical_drive_num'] = all_bytes[0]
        '''

    #
    # Parse FAT16 header
    #
    def parse_fat16_header(self):
        offset = self.offset_fat16_hdr
        self.fat16_hdr_logicaldrive_num = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.fat16_hdr_ext_sign = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.fat16_hdr_ser_num = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.fat16_hdr_vol_name = self.image[offset:offset+11]

        offset += 11
        self.fat16_hdr_fat_name = self.image[offset:offset+8]

        offset += 8
        self.fat16_hdr_exec_code = self.str2int(self.image[offset:offset+448])

        offset += 448
        self.fat16_hdr_exec_marker = self.str2int(self.image[offset:offset+2])

    #
    # Parse FAT16 entry
    #
    def parse_fat16_entry(self):
        #
        # Find directory entry
        #
        dir_table_start = (self.fat_common_hdr_secreserved + (self.fat_common_hdr_fatcopy_num * self.fat_common_hdr_secperfat)) * self.fat_common_hdr_bytespersec

        dir_table_len = self.fat_common_hdr_rootdirent_max * FAT_DIR_ENT_LEN

        self.find_fat16_dir_entry(dir_table_start, dir_table_len)

    #
    # Print FAT common header info
    #
    def print_fat_common_header_info(self):
        print("----------------------------------------")
        print("IMAGE COMMON HEADER INFO\n")
        print("                     Jump Code: %x" % self.fat_common_hdr_jumpcode + " (Hex)")
        print("                      OEM Name: " + str(self.fat_common_hdr_oem_name.strip()))
        print("              Bytes Per Sector: " + str(self.fat_common_hdr_bytespersec))
        print("            Sector Per Cluster: " + str(self.fat_common_hdr_secpercluster))
        print("               Sector Reserved: " + str(self.fat_common_hdr_secreserved))
        print("             FAT Copies Number: " + str(self.fat_common_hdr_fatcopy_num))
        print("Maximum Root Directory Entries: " + str(self.fat_common_hdr_rootdirent_max))
        print("      Small 32MB Sector Number: " + str(self.fat_common_hdr_small32mbsec_num))
        print("              Media Descriptor: " + str(hex(self.fat_common_hdr_mediadesc)))
        print("                Sector Per FAT: " + str(self.fat_common_hdr_secperfat))
        print("              Sector Per Track: " + str(self.fat_common_hdr_secpertrack))
        print("                   Head Number: " + str(self.fat_common_hdr_heads_num))
        print("          Hidden Sector Number: " + str(self.fat_common_hdr_hiddensec_num))
        print("                 Sector Number: " + str(self.fat_common_hdr_sec_num))

        print("")

    #
    # Print FAT16 header info
    #
    def print_fat16_header_info(self):
        print("----------------------------------------")
        print("IMAGE FAT16 HEADER INFO\n")
        print("Logical Drive Number: " + str(self.fat16_hdr_logicaldrive_num))
        print("       Ext Signature: " + str(self.fat16_hdr_ext_sign))
        print("       Serial Number: " + str(self.fat16_hdr_ser_num))
        print("         Volume Name: " + str(self.fat16_hdr_vol_name.strip()))
        print("            FAT Name: " + str(self.fat16_hdr_fat_name.strip()))
        #print("          Exec Code: %x" % self.fat16_hdr_exec_code + " (Hex)")
        print("           Exec Code: ignored here")
        print("         Exec Marker: %x" % self.fat16_hdr_exec_marker + " (Hex)")

        print("")

    #
    # Print FAT directory entry info
    #
    def print_fat_dir_entry(self, fat_dirent):
        print("----------------------------------------")
        print("IMAGE FAT16 DIRECTORY ENTRY INFO\n")
        print("              File Name: " + str(fat_dirent['file_name'].strip()))
        print("         File Extension: " + str(fat_dirent['file_ext'].strip()))
        print("         File Attribute: " + str(hex(fat_dirent['file_attr'])))
        print("         User Attribute: " + str(hex(fat_dirent['user_attr'])))
        print("   File Time Resolution: " + str(hex(fat_dirent['file_timeresolution'])))
        print("      File Time Created: " + str(hex(fat_dirent['file_timecreated'])))
        print("      File Date Created: " + str(hex(fat_dirent['file_datecreated'])))
        print("File Date Last Accessed: " + str(hex(fat_dirent['file_datelastaccessed'])))
        print("  File Access Right Map: " + str(hex(fat_dirent['file_accessrightmap'])))
        print("File Time Last Modified: " + str(hex(fat_dirent['file_timelastmodified'])))
        print("File Date Last Modified: " + str(hex(fat_dirent['file_datelastmodified'])))
        print("     File First Cluster: " + str(fat_dirent['file_firstcluster']))
        print("              File Size: " + str(fat_dirent['file_bytesize']) + " (bytes)")

        print("")

    #
    # Run routine
    #
    def run(self):
        #
        # Check image type ID
        #
        if self.check_fatimage_id() is False:
            print("\nERROR: invalid image type!\n")
            return

        #
        # Parse FAT common header
        #
        self.parse_fat_common_header()

        #
        # Print FAT common header info
        #
        self.print_fat_common_header_info()

        #
        # Check FAT type
        #
        fat_name = self.image[self.offset_fat16_hdr+18:self.offset_fat16_hdr+18+8]
        if fat_name.strip() == 'FAT16':
            #
            # Parse FAT16 header
            #
            self.parse_fat16_header()

            #
            # Print FAT16 header info
            #
            self.print_fat16_header_info()

            #
            # Parse FAT16 entry
            #
            self.parse_fat16_entry()
        else:
            #
            # Parse FAT32
            #
            pass

#
# Function Definition
#

#
# Parse image
#
def parse_fatimg(image_file):
    fp = open(image_file, "rb")

    image_data = fp.read()
    parser = FATParser(image_data)
    parser.run()

    fp.close()

    ''' test only
    print(hex(ord(image_data[0])))
    data_hex = binascii.b2a_hex(image_data[1])
    print(data_hex[0:4][::-1])
    '''

    return True

#
# Print usage
#
def print_usage():
    print("USAGE:\n")
    print("Parse FAT image: ./fatimg-parser.py fat.img\n")

    '''
    print("USAGE: python fatimg-parser.py [OPTION...]")
    print("Examples:")
    print("  python fatimg-parser.py -n=fat.img")
    print("Options:")
    print("  -d, --dir        Directory to be packed")
    print("  -n, --name       Container name")
    print("  -v, --verbose    Verbose messages")
    print("  -h, --help       Display help message")
    '''

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
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:n:vh", ["dir=", "name=", "verbose", "help"])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(1)

    '''
    for o, a in opts:
        if o in ("-d", "--dir"):
            pass
        elif o in ("-n", "--name"):
            pass
        elif o in ("-v", "--verbose"):
            pass
        elif o in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        else:
            assert False, "\nERROR: unhandled option!\n"
    '''

    args_len = len(args)
    if args_len is 1:
        if os.access(os.path.join(os.getcwd(), args[0]), os.F_OK) is True:
            print("\nParsing FAT image...\n")
            ret = parse_fatimg(os.path.join(os.getcwd(), args[0]))
            if ret is True:
                print("\nDone!\n")
            else:
                print("\nFailed!\n")
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
