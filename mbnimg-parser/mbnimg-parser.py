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
# To parse *.mbn:
# python mbnimg-parser.py test.mbn
#

import os, sys

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
# Image Type ID Class
#
class ImageType:
    NONE_IMG         = 0
    OEM_SBL_IMG      = 1
    AMSS_IMG         = 2
    QCSBL_IMG        = 3
    HASH_IMG         = 4
    APPSBL_IMG       = 5
    APPS_IMG         = 6
    HOSTDL_IMG       = 7
    DSP1_IMG         = 8 
    FSBL_IMG         = 9
    DBL_IMG          = 10
    OSBL_IMG         = 11
    DSP2_IMG         = 12
    EHOSTDL_IMG      = 13
    NANDPRG_IMG      = 14
    NORPRG_IMG       = 15
    RAMFS1_IMG       = 16
    RAMFS2_IMG       = 17
    ADSP_Q5_IMG      = 18
    APPS_KERNEL_IMG  = 19
    BACKUP_RAMFS_IMG = 20
    SBL1_IMG         = 21
    SBL2_IMG         = 22
    RPM_IMG          = 23
    SBL3_IMG         = 24
    TZ_IMG           = 25
    IMG_MAX          = 26

#
# Flash Partition Version
#
FLASH_PARTI_VERSION = 3

#
# Certification Chain Class
#
class CertChain:
    SIGNITURE = 0
    CERT      = 1
    CA        = 2
    ROOT      = 3

#
#  Certification Chain Attestation Cert Class
#
class AttestCert:
    C    = 0x130604550306
    ST   = 0x130804550306
    L    = 0x130704550306
    O    = 0x130B04550306
    CN   = 0x130A04550306
    INFO = 0x130304550306

#
# Certification Chain Signiture Calc Class
#
class SigCalc:
    SIGCALC = 0x140B04550306

#
# Class Definition For Parser
#
class Parser(object):
    def __init__(self, img):
        #
        # Init class member
        #
        self.image_id_tbl = {
            'appsbl': [ImageType.APPSBL_IMG, 'APPSBL_IMG', 'bin'],
            'dbl': [ImageType.DBL_IMG, 'DBL_IMG', 'bin'],
            'osbl': [ImageType.OSBL_IMG, 'OSBL_IMG', 'bin'],
            'amss': [ImageType.AMSS_IMG, 'AMSS_IMG', 'elf'],
            'amss_mbn': [ImageType.HASH_IMG, 'HASH_IMG', 'elf'],
            'apps': [ImageType.APPS_IMG, 'APPS_IMG', 'bin'],
            'hostdl': [ImageType.HOSTDL_IMG, 'HOSTDL_IMG', 'bin'],
            'ehostdl': [ImageType.EHOSTDL_IMG, 'EHOSTDL_IMG', 'bin'],
            'emmcbld': [ImageType.EHOSTDL_IMG, 'EMMCBLD_IMG', 'bin'],
            'qdsp6fw': [ImageType.DSP1_IMG, 'DSP1_IMG', 'elf'],
            'qdsp6sw': [ImageType.DSP2_IMG, 'DSP2_IMG', 'elf'],
            'qdsp5': [ImageType.ADSP_Q5_IMG, 'ADSP_Q5_IMG', 'bin'],
            'tz': [ImageType.TZ_IMG, 'TZ_IMG', 'bin'],
            'tzbsp_no_xpu': [ImageType.TZ_IMG, 'TZ_IMG', 'bin'],
            'tzbsp_with_test': [ImageType.TZ_IMG, 'TZ_IMG', 'bin'],
            'rpm': [ImageType.RPM_IMG, 'RPM_IMG', 'bin'],
            'sbl1': [ImageType.SBL1_IMG, 'SBL1_IMG', 'bin'],
            'sbl2': [ImageType.SBL2_IMG, 'SBL2_IMG', 'bin'],
            'sbl3': [ImageType.SBL3_IMG, 'SBL3_IMG', 'bin'],
            'efs1': [ImageType.RAMFS1_IMG, 'RAMFS1_IMG', 'bin'],
            'efs2': [ImageType.RAMFS2_IMG, 'RAMFS2_IMG', 'bin'],
            }

        self.image = img

        self.hdr_image_id = ""
        self.hdr_flash_parti_ver = FLASH_PARTI_VERSION
        self.hdr_image_src = 0x00000000
        self.hdr_image_dest_ptr = 0x00000000
        self.hdr_image_sz = 0x00000000
        self.hdr_code_sz = 0x00000000
        self.hdr_sig_ptr = 0x00000000
        self.hdr_sig_sz = 0x00000000
        self.hdr_cert_chain_ptr = 0x00000000
        self.hdr_cert_chain_sz = 0x00000000

        self.cert_chain_sig_sz = 0
        self.cert_chain_attestcert = []
        self.cert_chain_sigcalc = []

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
    # Check image ID
    #
    def check_image_id(self):
        image_id = self.str2int(self.image[0:4])

        if image_id >= ImageType.IMG_MAX:
            return False

        for index in self.image_id_tbl:
            if self.image_id_tbl[index][0] == image_id:
                 self.hdr_image_id = self.image_id_tbl[index][1]

    #
    # Parse header
    #
    def parse_header(self):
        offset = 4
        self.hdr_image_src = self.str2int(self.image[offset:offset+4])

        offset = 4
        self.hdr_flash_parti_ver = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_image_src = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_image_dest_ptr = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_image_sz = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_code_sz = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_sig_ptr = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_sig_sz = self.str2int(self.image[offset:offset+4])
        self.cert_chain_sig_sz = self.hdr_sig_sz

        offset += 4
        self.hdr_cert_chain_ptr = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.hdr_cert_chain_sz = self.str2int(self.image[offset:offset+4])

    #
    # Parse certification chain
    #
    def parse_cert_chain(self):
        offset = self.hdr_code_sz + self.hdr_sig_sz
        cert_cacert_rootcert_sz = self.hdr_image_sz - offset
        image_data = self.image[offset:offset+cert_cacert_rootcert_sz]

        index = 0
        for i in range(0, cert_cacert_rootcert_sz, 1):
            if self.str2int(image_data[i:i+6]) == AttestCert.C \
                    or self.str2int(image_data[i:i+6]) == AttestCert.ST \
                    or self.str2int(image_data[i:i+6]) == AttestCert.L \
                    or self.str2int(image_data[i:i+6]) == AttestCert.O \
                    or self.str2int(image_data[i:i+6]) == AttestCert.INFO:
                length = self.str2int(image_data[i+6])
                self.cert_chain_attestcert.append(image_data[i+7:i+7+length])

            elif self.str2int(image_data[i:i+6]) == SigCalc.SIGCALC:
                length = self.str2int(image_data[i+6])
                self.cert_chain_sigcalc.append(image_data[i+7:i+7+length])

    #
    # Print header info
    #
    def print_header_info(self):
        print("----------------------------------------")
        print("IMAGE HEADER INFO\n")
        print("              Image Type ID: " + self.hdr_image_id)
        print("        Flash Parti Version: " + str(self.hdr_flash_parti_ver))
        print("                  Image Src: " + str(hex(self.hdr_image_src)))
        print("              Image Dst Ptr: " + str(hex(self.hdr_image_dest_ptr)))
        print("                 Image Size: " + str(self.hdr_image_sz))
        print("            Image Code Size: " + str(self.hdr_code_sz))
        print("        Image Signiture Ptr: " + str(hex(self.hdr_sig_ptr)))
        print("       Image Signiture Size: " + str(self.hdr_sig_sz))
        print("    Certification Chain Ptr: " + str(hex(self.hdr_cert_chain_ptr)))
        print("   Certification Chain Size: " + str(self.hdr_cert_chain_sz))

        print("")

    #
    # Print certification chain info
    #
    def print_cert_chain_info(self):
        print("----------------------------------------")
        print("CERTIFICATION CHAIN INFO\n")
        print("                 Signiture:")
        print("                      Size: " + str(self.cert_chain_sig_sz))
        print("")
        print("          Attestation Cert:")
        print(self.cert_chain_attestcert)
        print("")
        print("            Signiture Calc:")
        print(self.cert_chain_sigcalc)
        print("")
        print("                 Root Cert: IGNORED HERE")

    #
    # Run routine
    #
    def run(self):
        #
        # Check image type ID
        #
        if self.check_image_id() is False:
            print("\nERROR: invalid image type!\n")
            return

        #
        # Parse header
        #
        self.parse_header()

        #
        # Parse certification chain
        #
        self.parse_cert_chain()

        #
        # Print header info
        #
        self.print_header_info()

        #
        # Print certification chain info
        #
        self.print_cert_chain_info()

#
# Function Definition
#

#
# Parse *.mbn image
#
def parse_mbnimg(image_file):
    fp = open(image_file, "rb")

    image_data = fp.read()
    parser = Parser(image_data)
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
    print("Parse *.mbn image: ./mbnimg-parser.py tz.mbn\n")

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
        if os.access(os.path.join(os.getcwd(), args[1]), os.F_OK) is True:
            print("\nParsing *.mbn image...\n")
            ret = parse_mbnimg(os.path.join(os.getcwd(), args[1]))
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
