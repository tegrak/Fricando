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
# python mbnimg-parser.py -f test.mbn -v -s sigverify-list.txt
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
# Verify signature in image
#
is_sig_verified = False
sigverify_list = ""

#
# Maximum size of flash Auto-detected page
#
FLASH_AUTO_DETECT_MAX_PAGE = 8192

#
# Minimum size of flash Auto-detected page
#
FLASH_AUTO_DETECT_MIN_PAGE = 2048

#
# Size of flash Auto-detected page
#
FLASH_AUTO_DETECT_PAGE_SZ = FLASH_AUTO_DETECT_MIN_PAGE

#
# Number of flash Auto-detected page
#
FLASH_AUTO_DETECT_PAGE_NUM = FLASH_AUTO_DETECT_MAX_PAGE / FLASH_AUTO_DETECT_MIN_PAGE

#
# Size of flash Auto-detected page padding
#
FLASH_AUTO_DETECT_PAGE_PADDING_SZ = FLASH_AUTO_DETECT_MIN_PAGE

#
# Flash Partition Version
#
FLASH_PARTI_VERSION = 3

#
# Image Magic Info For SBL1 Image Class
#
class ImageMagic:
    FLASH_CODE_WORD                  = 0x844BDCD1
    UNIFIED_BOOT_COOKIE_MAGIC_NUMBER = 0x33836685
    MAGIC_NUM                        = 0x73D71034
    AUTODETECT_PAGE_SIZE_MAGIC_NUM   = 0x7D0B435A

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
# Certification Chain Class
#
class CertChain:
    SIGNATURE = 0
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
# Certification Chain Signature Calc Class
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

        self.is_sbl1_image = False

        #
        # SBL1 preamble info definition
        #
        self.preamble_flash_code = ImageMagic.FLASH_CODE_WORD
        self.preamble_magic_num = ImageMagic.MAGIC_NUM
        self.preamble_pagesz_magic_num = ImageMagic.AUTODETECT_PAGE_SIZE_MAGIC_NUM

        #
        # SBL1 header info definition
        #
        self.hdr_codeword = ImageMagic.FLASH_CODE_WORD
        self.hdr_magic = ImageMagic.MAGIC_NUM
        self.hdr_reserved_0 = 0x00000000
        self.hdr_reserved_1 = 0x00000000
        self.hdr_reserved_2 = 0x00000000
        self.hdr_oem_root_cert_sel = 0
        self.hdr_oem_num_root_certs = 0
        self.hdr_reserved_3 = 0x00000000
        self.hdr_reserved_4 = 0x00000000
        self.hdr_reserved_5 = 0x00000000

        #
        # Header info definition except SBL1 image
        #
        self.hdr_image_id = ""
        self.hdr_flash_parti_ver = FLASH_PARTI_VERSION

        #
        # Header info definition for all mbn images
        #
        self.hdr_image_src = 0x00000000
        self.hdr_image_dest_ptr = 0x00000000
        self.hdr_image_sz = 0x00000000
        self.hdr_code_sz = 0x00000000
        self.hdr_sig_ptr = 0x00000000
        self.hdr_sig_sz = 0x00000000
        self.hdr_cert_chain_ptr = 0x00000000
        self.hdr_cert_chain_sz = 0x00000000
        ''' DISUSED
        self.hdr_magic_num = 0x00000000
        self.hdr_version = 0x00000000
        self.hdr_os_type = 0x00000000
        self.hdr_boot_apps_parti_entry = 0x00000000
        self.hdr_boot_apps_size_entry = 0x00000000
        self.hdr_boot_apps_ram_loc = 0x00000000
        self.hdr_reserved_ptr = 0x00000000
        self.hdr_reserved_6 = 0x00000000
        self.hdr_reserved_7 = 0x00000000
        self.hdr_reserved_8 = 0x00000000
        '''

        #
        # Certification chain definition
        #
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

        if image_id == ImageMagic.FLASH_CODE_WORD:
            #
            # Check SBL1 image ID first
            #
            self.preamble_flash_code = image_id
            self.is_sbl1_image = True

        elif image_id < ImageType.IMG_MAX:
            #
            # Check image ID except SBL1 image
            #
            for index in self.image_id_tbl:
                if self.image_id_tbl[index][0] == image_id:
                    self.hdr_image_id = self.image_id_tbl[index][1]

        else:
            return False

        return True

    #
    # Parse header
    #
    def parse_header(self):
        if self.is_sbl1_image is True:
            offset = 4
            self.preamble_magic_num = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.preamble_pagesz_magic_num = self.str2int(self.image[offset:offset+4])

            offset += 4

            offset = FLASH_AUTO_DETECT_PAGE_SZ * FLASH_AUTO_DETECT_PAGE_NUM + FLASH_AUTO_DETECT_PAGE_PADDING_SZ
            self.hdr_codeword = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_magic = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_0 = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_1 = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_2 = self.str2int(self.image[offset:offset+4])
        else:
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

        if self.is_sbl1_image is True:
            offset += 4
            self.hdr_oem_root_cert_sel = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_oem_num_root_certs = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_3 = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_4 = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_5 = self.str2int(self.image[offset:offset+4])
        else:
            pass
            ''' DISUSED
            offset += 4
            self.hdr_magic_num = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_version = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_os_type = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_boot_apps_parti_entry = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_boot_apps_size_entry = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_boot_apps_ram_loc = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_ptr = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_6 = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_7 = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.hdr_reserved_8 = self.str2int(self.image[offset:offset+4])
            '''

    #
    # Parse certification chain
    #
    def parse_cert_chain(self):
        offset = self.hdr_code_sz + self.hdr_sig_sz
        cert_cacert_rootcert_sz = self.hdr_image_sz - offset
        image_data = self.image[self.hdr_image_src+offset:self.hdr_image_src+offset+cert_cacert_rootcert_sz]

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

        if self.is_sbl1_image is True:
            print("Preamble Flash Code     : " + str(hex(self.preamble_flash_code)))
            print("Preamble Magic          : " + str(hex(self.preamble_magic_num)))
            print("Preamble Page Size Magic: " + str(hex(self.preamble_pagesz_magic_num)))
            print("Code Word               : " + str(hex(self.hdr_codeword)))
            print("Magic                   : " + str(hex(self.hdr_magic)))
        else:
            print("Image Type ID           : " + self.hdr_image_id)
            print("Flash Parti Version     : " + str(self.hdr_flash_parti_ver))

        print("Image Src               : " + str(hex(self.hdr_image_src)))
        print("Image Dst Ptr           : " + str(hex(self.hdr_image_dest_ptr)))
        print("Image Size              : " + str(self.hdr_image_sz))
        print("Code Size               : " + str(self.hdr_code_sz))
        print("Signature Ptr           : " + str(hex(self.hdr_sig_ptr)))
        print("Signature Size          : " + str(self.hdr_sig_sz))
        print("Certification Chain Ptr : " + str(hex(self.hdr_cert_chain_ptr)))
        print("Certification Chain Size: " + str(self.hdr_cert_chain_sz))

        if self.is_sbl1_image is True:
            print("OEM Root Cert Select    : " + str(self.hdr_oem_root_cert_sel))
            print("OEM Root Certs Num      : " + str(self.hdr_oem_num_root_certs))
        else:
            pass
            ''' DISUSED
            print("Magic Num               : " + str(hex(self.hdr_magic_num)))

            print("Version                 : " + str(hex(self.hdr_version)))

            print("OS Type                 : " + str(hex(self.hdr_os_type)))

            print("Boot Apps Parti Entry   : " + str(hex(self.hdr_boot_apps_parti_entry)))

            print("Boot Apps Size Entry    : " + str(hex(self.hdr_boot_apps_size_entry)))

            print("Boot Apps RAM location  : " + str(hex(self.hdr_boot_apps_ram_loc)))
            '''

        print("")

    #
    # Print certification chain info
    #
    def print_cert_chain_info(self):
        print("----------------------------------------")
        print("CERTIFICATION CHAIN INFO\n")
        print("Signature       :")
        print("Size            : " + str(self.cert_chain_sig_sz))
        print("")
        print("Attestation Cert:")
        print(self.cert_chain_attestcert)
        print("")
        print("Signature Calc  :")
        print(self.cert_chain_sigcalc)
        print("")
        print("Root Cert       : IGNORED HERE")

    #
    # Run routine
    #
    def run(self):
        global is_pr_verb

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
        if is_pr_verb is True:
            self.print_header_info()

        #
        # Print certification chain info
        #
        if is_pr_verb is True:
            self.print_cert_chain_info()

    #
    # Get certifiaction chain signature size
    #
    def get_cert_chain_sig_sz(self):
        return self.cert_chain_sig_sz

    #
    # Get certifiaction chain attest cert
    #
    def get_cert_chain_attestcert(self):
        return self.cert_chain_attestcert

    #
    # Get certifiaction chain signature calc
    #
    def get_cert_chain_sigcalc(self):
        return self.cert_chain_sigcalc

#
# Function Definition
#

#
# Verify if attest cert is in mbn image
#
def is_attestcert_in_sigverify_list(attestcertlist, certname):
    if certname in attestcertlist:
        return True
    else:
        return False

#
# Verify attest cert in mbn image
#
def verify_attestcert_in_sigverify_list(attestcert_list):
    global sigverify_list

    for item in sigverify_list:
        if is_attestcert_in_sigverify_list(attestcert_list, item) is False:
            return False
        else:
            continue

    return True

#
# Parse signature verification list
#
def parse_sigverify_list(sv_list_file):
    sv_list = []

    fp = open(sv_list_file, "rb")
    fp_data = fp.readlines()
    fp.close()

    for item in fp_data:
        item_list = item.strip('\n').split(' ')

        for i in item_list:
            if i != '':
                sv_list.append(i)

    return sv_list

#
# Parse *.mbn image
#
def parse_mbnimg(image_file):
    global is_sig_verified

    ret = False

    fp = open(image_file, "rb")
    image_data = fp.read()
    fp.close()

    parser = Parser(image_data)
    parser.run()

    if is_sig_verified is True:
        print("\nVerifying signature in mbn image...")

        attestcert_list = parser.get_cert_chain_attestcert()

        ret = verify_attestcert_in_sigverify_list(attestcert_list)
        if ret is True:
            print("The image is signed.")
        else:
            print("The image is NOT signed!")
    else:
        ret = True

    ''' test only
    print(hex(ord(image_data[0])))
    data_hex = binascii.b2a_hex(image_data[1])
    print(data_hex[0:4][::-1])
    '''

    return ret

#
# Print usage
#
def print_usage():
    print("USAGE: python mbnimg-parser.py [OPTION...]")
    print("")
    print("EXAMPLES:")
    print("  python mbnimg-parser.py -f sample.mbn -s sigverify-list.txt")
    print("")
    print("OPTIONS:")
    print("  -f, --file       Image file to be parsed")
    print("  -s, --sigverify  Verify signature")
    print("  -v, --verbose    Verbose messages")
    print("  -h, --help       Display help message")
    print("")

#
# Main Entry
#
def main():
    global is_pr_verb
    global is_sig_verified
    global sigverify_list

    ret = False

    sv_list = ""

    #
    # Display banner
    #
    print(banner)

    #
    # Get args list
    #
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:s:vh", ["file=", "sigverify=", "verbose", "help"])
    except getopt.GetoptError, err:
        print str(err)
        print_usage()
        sys.exit(1)

    for o, a in opts:
        if o in ("-f", "--file"):
            image_file = a
        elif o in ("-s", "--sigverify"):
            is_sig_verified = True
            sv_list = a
        elif o in ("-v", "--verbose"):
            is_pr_verb = True
        elif o in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        else:
            continue

    #
    # Sanity check for '-s'
    #
    if is_sig_verified is True:
        if os.access(os.path.join(os.getcwd(), sv_list), os.F_OK) is True:
            sigverify_list = parse_sigverify_list(sv_list)
            if len(sigverify_list) == 0:
                print("\nERROR: '%s' is empty!\n" % sv_list)
                print_usage()
                sys.exit(1)
        else:
            print("\nERROR: invalid parameter '%s' !\n" % sv_list)
            print_usage()
            sys.exit(1)

    #
    # Parse mbn image
    #
    if os.access(os.path.join(os.getcwd(), image_file), os.F_OK) is True:
        print("\nParsing mbn image...\n")
        ret = parse_mbnimg(os.path.join(os.getcwd(), image_file))
        if ret is True:
            print("\nDone!\n")
        else:
            print("\nFailed!\n")
    else:
        print("\nERROR: invalid parameter '%s' !\n" % image_file)
        print_usage()
        sys.exit(1)

    return ret

#
# App Entry
#
if __name__ == '__main__':
    main()
