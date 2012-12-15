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
# To parse Ext4 image:
# python ext4img-parser.py -f ext4.img -v -d ext4-dump
#

import os, sys
import getopt

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
# Display verbose messages
#
is_pr_verb = False

#
# Dump Ext4 image into local directory
#
is_ext4_dumped = False
ext4_dumpdir = ""

#
# Ext4 Parameters
#

#
# Class Definition For Ext4 Parser
#
class Ext4Parser(object):
    def __init__(self, img):
        #
        # Init class member
        #
        self.image = img

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
    # Check Ext4 image ID
    #
    def check_ext4image_id(self):
        pass

    #
    # Run routine
    #
    def run(self):
        global is_pr_verb

        #
        # Check image type ID
        #
        if self.check_ext4image_id() is False:
            print("\nERROR: invalid image type!\n")
            return

    #
    # Dump Ext4 image file to directory
    #
    def dumpto(self, dumpdir):
        return True

#
# Function Definition
#

#
# Parse image
#
def parse_ext4img(image_file):
    global is_ext4_dumped
    global ext4_dumpdir

    fp = open(image_file, "rb")
    image_data = fp.read()
    fp.close()

    parser = Ext4Parser(image_data)
    parser.run()

    if is_ext4_dumped is True:
        print("\nDumping files from Ext4 image...")

        ret = parser.dumpto(ext4_dumpdir)
        if ret is True:
            print("All files dumped.")
        else:
            print("Failed to dump files!")

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
    print("USAGE: python ext4img-parser.py [OPTION...]")
    print("")
    print("EXAMPLES:")
    print("  python ext4img-parser.py -f ext4.img -v -d ext4-dump")
    print("")
    print("OPTIONS:")
    print("  -f, --file       Image file to be parsed")
    print("  -d, --dump       Dump image file to directory")
    print("  -v, --verbose    Verbose messages")
    print("  -h, --help       Display help message")
    print("")

#
# Main Entry
#
def main():
    global is_pr_verb
    global is_ext4_dumped
    global ext4_dumpdir

    image_file = ""

    #
    # Display banner
    #
    print(banner)

    #
    # Get args list
    #
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:d:vh", ["file=", "dump=", "verbose", "help"])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(1)

    for o, a in opts:
        if o in ("-f", "--file"):
            image_file = a
        elif o in ("-d", "--dump"):
            is_ext4_dumped = True
            ext4_dumpdir = a
        elif o in ("-v", "--verbose"):
            is_pr_verb = True
        elif o in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        else:
            continue

    #
    # Sanity check for '-d'
    #
    if is_ext4_dumped is True:
        if os.access(os.path.join(os.getcwd(), ext4_dumpdir), os.F_OK) is False:
            os.makedirs(os.path.join(os.getcwd(), ext4_dumpdir))

            #print("\nINFO: '%s' not exist and creat it now\n" % ext4_dumpdir)

            if os.access(os.path.join(os.getcwd(), ext4_dumpdir), os.F_OK) is False:
                print("\nERROR: invalid parameter '%s' !\n" % ext4_dumpdir)
                print_usage()
                sys.exit(1)

    #
    # Parse Ext4 image
    #
    if os.access(os.path.join(os.getcwd(), image_file), os.F_OK) is True:
        print("\nParsing Ext4 image...\n")
        ret = parse_ext4img(os.path.join(os.getcwd(), image_file))
        if ret is True:
            print("\nDone!\n")
        else:
            print("\nFailed!\n")
    else:
        print("\nERROR: invalid parameter '%s' !\n" % image_file)
        print_usage()
        sys.exit(1)

#
# App Entry
#
if __name__ == '__main__':
    main()
