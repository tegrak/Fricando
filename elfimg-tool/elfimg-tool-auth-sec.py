#!/usr/bin/env python
#
# Copyright (c) 2013-2014 angersax@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (in the main directory of the distribution
# in the file COPYING); if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  US
#

'''
Example:

To generate ELF with signature and certificate chain according to directory:
python elfimg-tool-auth-sec.py -d /path/to/dir-of-sample -s /path/to/dir-of-signature-tool -b kmod_auth_sec
'''

import os, sys
import getopt
import struct
import hashlib
import subprocess
from stat import *
from zipfile import ZipFile

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

class FileType:
  KMODULE = 0

filetype_table = {
  'ko': [FileType.KMODULE, '.ko']
}

'''
Certificate Definitions
'''
PAD_BYTE_1            = 255       # Padding byte 1s
PAD_BYTE_0            = 0         # Padding byte 0s
SHA256_SIGNATURE_SIZE = 256       # Support SHA256
CERT_CHAIN_MAXSIZE    = 6 * 1024  # Maximum size of certificate chain
MAX_NUM_ROOT_CERTS    = 4         # Maximum number of OEM root certificates 
MI_BOOT_IMG_HDR_SIZE  = 40        # sizeof(mi_boot_image_header_type)
BOOT_HEADER_LENGTH    = 20        # Boot Header Number of Elements
FLASH_PARTI_VERSION   = 3         # Flash Partition Version Number
MAX_PHDR_COUNT        = 10        # Maximum allowable program headers

'''
ELF Definitions
'''
ELF_HDR_SIZE            = 52
ELF_PHDR_SIZE           = 32
ELF_SHDR_SIZE           = 40
ELFINFO_MAG0_INDEX      = 0
ELFINFO_MAG1_INDEX      = 1
ELFINFO_MAG2_INDEX      = 2
ELFINFO_MAG3_INDEX      = 3
ELFINFO_MAG0            = '\x7f'
ELFINFO_MAG1            = 'E'
ELFINFO_MAG2            = 'L'
ELFINFO_MAG3            = 'F'
ELFINFO_CLASS_INDEX     = 4
ELFINFO_CLASS_32        = '\x01'
ELFINFO_VERSION_INDEX   = 6
ELFINFO_VERSION_CURRENT = '\x01'
ELF_BLOCK_ALIGN         = 0x1000

'''
ELF Object File Types
'''
ET_NONE   = 0
ET_REL    = 1
ET_EXEC   = 2
ET_DYN    = 3
ET_CORE   = 4
ET_LOPROC = 0xFF00
ET_HIPROC = 0xFFFF

'''
ELF Machine Types (part)
'''
EM_NONE  = 0
EM_386   = 3
EM_ARM   = 40
EM_QDSP6 = 164

'''
ELF Version
'''
EV_NONE    = 0
EV_CURRENT = 1

'''
ELF Flags
'''
EF_ARM_HASENTRY         = 0x02
EF_ARM_V4               = 0x03
EF_ARM_SYMSARESORTED    = 0x04
EF_ARM_DYNSYMSUSESEGIDX = 0x08
EF_ARM_MAPSYMSFIRST     = 0x10
EF_ARM_EABIMASK         = 0xFF000000

'''
ELF Program Header Types
'''
NULL_TYPE    = 0x0
LOAD_TYPE    = 0x1
DYNAMIC_TYPE = 0x2
INTERP_TYPE  = 0x3
NOTE_TYPE    = 0x4
SHLIB_TYPE   = 0x5
PHDR_TYPE    = 0x6
TLS_TYPE     = 0x7

'''
ELF Program Segment Types
'''
PT_NULL    = 0
PT_LOAD    = 1
PT_DYNAMIC = 2
PT_INTERP  = 3
PT_NOTE    = 4
PT_SHLIB   = 5
PT_PHDR    = 6
PT_LOPROC  = 0x70000000
PT_HIPROC  = 0x7FFFFFFF

'''
Helper defines to help parse ELF program headers
'''
MI_PROG_BOOT_DIGEST_SIZE       = 20

'''
Segment Type
'''
MI_PBT_HASH_SEGMENT      = 0x2
MI_PBT_PHDR_SEGMENT      = 0x7

'''
Access Type
'''
MI_PBT_RW_SEGMENT      = 0x0
MI_PBT_RO_SEGMENT      = 0x1
MI_PBT_ZI_SEGMENT      = 0x2
MI_PBT_NOTUSED_SEGMENT = 0x3
MI_PBT_SHARED_SEGMENT  = 0x4

'''
ELF Segment Flag Definitions
'''
MI_PBT_ELF_HASH_SEGMENT = 0x02200000 
MI_PBT_ELF_PHDR_SEGMENT = 0x07000000 

'''
Class of Image Type ID
'''
class ImageType:
  NONE_IMG         = 0
  HASH_IMG         = 4

'''
Image Type Table
'''
image_id_table = {
  'hash': [ImageType.HASH_IMG, 'HASH_IMG', 'bin'],
} 

'''
Class of ELF Header
'''
class Elf32_Ehdr:
  s = struct.Struct('16sHHIIIIIHHHHHH') 

  def __init__(self, data):
      unpacked_data       = (Elf32_Ehdr.s).unpack(data)
      self.unpacked_data  = unpacked_data
      self.e_ident        = unpacked_data[0]
      self.e_type         = unpacked_data[1]
      self.e_machine      = unpacked_data[2]
      self.e_version      = unpacked_data[3]
      self.e_entry        = unpacked_data[4]
      self.e_phoff        = unpacked_data[5]
      self.e_shoff        = unpacked_data[6]
      self.e_flags        = unpacked_data[7]
      self.e_ehsize       = unpacked_data[8]
      self.e_phentsize    = unpacked_data[9]
      self.e_phnum        = unpacked_data[10]
      self.e_shentsize    = unpacked_data[11]
      self.e_shnum        = unpacked_data[12]
      self.e_shstrndx     = unpacked_data[13]

  def __del__(self):
    pass

  def printValues(self):
    print >> sys.stdout, "ATTRIBUTE / VALUE"
    for attr, value in self.__dict__.iteritems():
      print >> sys.stdout, attr, value

  def getPackedData(self):
    values = [self.e_ident,
              self.e_type,
              self.e_machine,
              self.e_version,
              self.e_entry,
              self.e_phoff,
              self.e_shoff,
              self.e_flags,
              self.e_ehsize,
              self.e_phentsize,
              self.e_phnum,
              self.e_shentsize,
              self.e_shnum,
              self.e_shstrndx
              ]

    return (Elf32_Ehdr.s).pack(*values)

'''
ELF Program Header Class
'''
class Elf32_Phdr:
  s = struct.Struct('I' * 8)

  def __init__(self, data):
    unpacked_data       = (Elf32_Phdr.s).unpack(data)
    self.unpacked_data  = unpacked_data
    self.p_type         = unpacked_data[0]
    self.p_offset       = unpacked_data[1]
    self.p_vaddr        = unpacked_data[2]
    self.p_paddr        = unpacked_data[3]
    self.p_filesz       = unpacked_data[4]
    self.p_memsz        = unpacked_data[5]
    self.p_flags        = unpacked_data[6]
    self.p_align        = unpacked_data[7]

  def __del__(self):
    pass

  def printValues(self):
    print >> sys.stdout, "ATTRIBUTE / VALUE"
    for attr, value in self.__dict__.iteritems():
      print >> sys.stdout, attr, value

  def getPackedData(self):
    values = [self.p_type,
              self.p_offset,
              self.p_vaddr,
              self.p_paddr,
              self.p_filesz,
              self.p_memsz,
              self.p_flags,
              self.p_align
              ]

    return (Elf32_Phdr.s).pack(*values)

'''
ELF Segment Information Class
'''
class SegmentInfo:
  def __init__(self):
    self.flag  = 0
    self.start_addr = 0

  def __del__(self):
    pass

  def printValues(self):
    print >> sys.stdout, 'Flag: ' + str(self.flag)
    print >> sys.stdout, 'Start Address: ' + str(hex(self.start_addr))

'''
Regular Boot Header Class
'''
class Boot_Hdr:
  s_part = struct.Struct('I' * 10)
  s_full = struct.Struct('I' * BOOT_HEADER_LENGTH)

  def __init__(self, init_val):
    self.image_id = ImageType.NONE_IMG
    self.flash_parti_ver = FLASH_PARTI_VERSION
    self.image_src = init_val  
    self.image_dest_ptr = init_val  
    self.image_size = init_val  
    self.code_size = init_val 
    self.sig_ptr = init_val  
    self.sig_size = init_val  
    self.cert_chain_ptr = init_val  
    self.cert_chain_size = init_val  
    self.magic_number1 = init_val  
    self.version = init_val  
    self.OS_type = init_val 
    self.boot_apps_parti_entry = init_val  
    self.boot_apps_size_entry = init_val  
    self.boot_apps_ram_loc = init_val 
    self.reserved_ptr = init_val  
    self.reserved_1 = init_val 
    self.reserved_2 = init_val 
    self.reserved_3 = init_val 

  def __del__(self):
    pass

  def getLength(self):
    return BOOT_HEADER_LENGTH
 
  def writePackedData(self, target, write_full_hdr):  
    values = [self.image_id,
              self.flash_parti_ver,
              self.image_src,
              self.image_dest_ptr,
              self.image_size,
              self.code_size ,
              self.sig_ptr,
              self.sig_size,
              self.cert_chain_ptr,
              self.cert_chain_size,
              self.magic_number1,
              self.version,
              self.OS_type,
              self.boot_apps_parti_entry,
              self.boot_apps_size_entry,
              self.boot_apps_ram_loc,
              self.reserved_ptr,
              self.reserved_1,
              self.reserved_2,
              self.reserved_3 ]

    '''
    Write 10 entries(40B) or 20 entries(80B) of boot header
    '''
    if write_full_hdr is False:
      s = struct.Struct('I'* 10)
      values = values[:10]
    else:
      s = struct.Struct('I' * self.getLength())

      packed_data = s.pack(*values)

      fp = open(target,'wb')
      fp.write(packed_data)
      fp.close()

      return s.size

'''
Class of ELF Builder
'''
class ElfBuilder(object):
  def __init__(self, srcname, dstname, signtool = None, namebase = None):
    self.ehdr = Elf32_Ehdr('\0' * ELF_HDR_SIZE)
    self.phdr = Elf32_Phdr('\0' * ELF_PHDR_SIZE)
    self.bhdr = Boot_Hdr(int('0x0', 16))
    self.src_fp = -1
    self.src_sz = os.stat(srcname).st_size
    self.dst_fp = -1
    self.signtool = signtool
    self.namebase = namebase

    self.initialize(srcname, dstname)

  def initialize(self, srcname, dstname):
    try:
      self.src_fp = open(srcname, 'rb')
      self.dst_fp = open(dstname, 'wb+')
    except IOError, err:
      print >> sys.stderr, str(err)
      raise os.error

    try:
      self.build()
      self.flush()
    except OSError, err:
      print >> sys.stderr, str(err)
      self.src_fp.close()
      self.dst_fp.close()
      os.remove(dstname)
      raise os.error

  def __del__(self):
    if self.src_fp != -1:
      self.src_fp.close()

    if self.dst_fp != -1:
      self.dst_fp.close()

  '''
  Generate hash

  if sizeof(buf) < ELF_BLOCK_ALIGN:
    hash_size = sizeof(buf)
  else:
    hash_size = ELF_BLOCK_ALIGN
  '''
  def gen_sha1_hash(self, buf):
    m = hashlib.sha1()
    m.update(buf)
    return m.digest()

  '''
  Unzip .zip file
  '''
  def unzip(self, zipname, dirname):
    z = ZipFile(zipname, 'r')
    names = z.namelist()
    for name in names:
      outfile = file(os.path.sep.join((dirname, name)), 'wb+')
      outfile.write(z.read(name))
      outfile.close()
    z.close()

  '''
  Write ELF header
  '''
  def write_exec_ehdr(self, entry, phnum):
    self.ehdr.e_ident     = \
        ELFINFO_MAG0 \
        + ELFINFO_MAG1 \
        + ELFINFO_MAG2 \
        + ELFINFO_MAG3 \
        + ELFINFO_CLASS_32 \
        + '\x01' \
        + ELFINFO_VERSION_CURRENT \
        + '\x00' * 9
    self.ehdr.e_type      = ET_EXEC
    self.ehdr.e_machine   = EM_QDSP6
    self.ehdr.e_version   = EV_CURRENT
    self.ehdr.e_entry     = entry
    self.ehdr.e_phoff     = ELF_HDR_SIZE
    self.ehdr.e_shoff     = 0
    self.ehdr.e_flags     = EF_ARM_V4
    self.ehdr.e_ehsize    = ELF_HDR_SIZE
    self.ehdr.e_phentsize = ELF_PHDR_SIZE
    self.ehdr.e_phnum     = phnum
    self.ehdr.e_shentsize = ELF_SHDR_SIZE
    self.ehdr.e_shnum     = 0
    self.ehdr.e_shstrndx  = 0

    values = [self.ehdr.e_ident,
              self.ehdr.e_type,
              self.ehdr.e_machine,
              self.ehdr.e_version,
              self.ehdr.e_entry,
              self.ehdr.e_phoff,
              self.ehdr.e_shoff,
              self.ehdr.e_flags,
              self.ehdr.e_ehsize,
              self.ehdr.e_phentsize,
              self.ehdr.e_phnum,
              self.ehdr.e_shentsize,
              self.ehdr.e_shnum,
              self.ehdr.e_shstrndx
              ]

    packed_values = Elf32_Ehdr.s.pack(*values)

    offset = 0
    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write(packed_values)

    return 0

  '''
  Write ELF program header table
  '''
  def write_phdr_tbl(self):
    '''
    Write ELF program header
    '''
    ret = self.write_progheader_phdr()
    if ret != 0:
      return -1

    '''
    Write ELF hash table header
    '''
    '''
    Add boot image header at head of hast table
    '''
    hash_tbl_size = MI_BOOT_IMG_HDR_SIZE

    '''
    Add hash segment for program header
    '''
    hash_tbl_size += MI_PROG_BOOT_DIGEST_SIZE

    '''
    Add hash segment for the hash table itself
    '''
    hash_tbl_size += MI_PROG_BOOT_DIGEST_SIZE

    '''
    Add hash segment for code segment
    '''
    hash_tbl_size += MI_PROG_BOOT_DIGEST_SIZE

    '''
    Add other hash segment
    Add code here
    '''

    '''
    Add signature & certificate
    '''
    hash_tbl_size += SHA256_SIGNATURE_SIZE
    hash_tbl_size += CERT_CHAIN_MAXSIZE

    '''
    Add code here
    vaddr
    '''
    '''
    'offset = ELF_BLOCK_ALIGN' disused due to customized definition
    '''
    offset = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize)

    vaddr  = 0
    paddr  = vaddr
    filesz = hash_tbl_size
    memsz  = 0
    ret = self.write_hashtbl_phdr(offset, vaddr, paddr, filesz, memsz)
    if ret != 0:
      return -1

    '''
    Write ELF code segment header
    Add code here
    '''
    type = NULL_TYPE

    '''
    Check if segment size is block aligned
    '''
    '''
    'if (hash_tbl_size > ELF_BLOCK_ALIGN)' disused due to customized definition
    '''
    size = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize) + hash_tbl_size
    if (size > ELF_BLOCK_ALIGN):
      off = size & (ELF_BLOCK_ALIGN - 1)
      if (int(off) != 0):
        pad = ELF_BLOCK_ALIGN - off
    else:
      pad = ELF_BLOCK_ALIGN - size

    '''
    'offset = ELF_BLOCK_ALIGN + hash_tbl_size + pad'
    disused due to customized definition
    '''
    offset = size + pad

    vaddr  = 0
    paddr  = vaddr
    filesz = self.src_sz
    memsz  = 0
    flags  = MI_PBT_ELF_PHDR_SEGMENT
    ret = self.write_codeseg_phdr(type, offset, vaddr, paddr, filesz, memsz, flags)
    if ret != 0:
      return -1

    '''
    Write ELF other header
    Add code here
    '''

    return 0

  '''
  Write ELF program header
  '''
  def write_progheader_phdr(self):
    self.phdr.p_type   = NULL_TYPE
    self.phdr.p_offset = 0
    self.phdr.p_vaddr  = 0
    self.phdr.p_paddr  = 0
    self.phdr.p_filesz = self.ehdr.e_ehsize + (self.ehdr.e_phnum * self.ehdr.e_phentsize)
    self.phdr.p_memsz  = 0
    self.phdr.p_flags  = MI_PBT_ELF_PHDR_SEGMENT
    self.phdr.p_align  = 0

    values = [self.phdr.p_type,
              self.phdr.p_offset,
              self.phdr.p_vaddr,
              self.phdr.p_paddr,
              self.phdr.p_filesz,
              self.phdr.p_memsz,
              self.phdr.p_flags,
              self.phdr.p_align
              ]

    packed_values = Elf32_Phdr.s.pack(*values)

    offset = self.ehdr.e_ehsize
    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write(packed_values)

    return 0

  '''
  Write ELF hash table header
  '''
  def write_hashtbl_phdr(self, offset, vaddr, paddr, filesz, memsz):
    self.phdr.p_type   = LOAD_TYPE
    self.phdr.p_offset = offset
    self.phdr.p_vaddr  = vaddr
    self.phdr.p_paddr  = paddr
    self.phdr.p_filesz = filesz
    self.phdr.p_memsz  = memsz
    self.phdr.p_flags  = MI_PBT_ELF_HASH_SEGMENT
    self.phdr.p_align  = ELF_BLOCK_ALIGN

    values = [self.phdr.p_type,
              self.phdr.p_offset,
              self.phdr.p_vaddr,
              self.phdr.p_paddr,
              self.phdr.p_filesz,
              self.phdr.p_memsz,
              self.phdr.p_flags,
              self.phdr.p_align
              ]

    packed_values = Elf32_Phdr.s.pack(*values)

    offset = self.ehdr.e_phoff + self.ehdr.e_phentsize
    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write(packed_values)

    return 0

  '''
  Write ELF code segment header
  '''
  def write_codeseg_phdr(self, type, offset, vaddr, paddr, filesz, memsz, flags):
    self.phdr.p_type   = type
    self.phdr.p_offset = offset
    self.phdr.p_vaddr  = vaddr
    self.phdr.p_paddr  = paddr
    self.phdr.p_filesz = filesz
    self.phdr.p_memsz  = memsz
    self.phdr.p_flags  = flags
    self.phdr.p_align  = ELF_BLOCK_ALIGN

    values = [self.phdr.p_type,
              self.phdr.p_offset,
              self.phdr.p_vaddr,
              self.phdr.p_paddr,
              self.phdr.p_filesz,
              self.phdr.p_memsz,
              self.phdr.p_flags,
              self.phdr.p_align
              ]

    packed_values = Elf32_Phdr.s.pack(*values)

    offset = self.ehdr.e_phoff + (self.ehdr.e_phentsize * 2)
    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write(packed_values)

    return 0

  '''
  Write Hash table
  '''
  def write_hash_tbl(self):
    '''
    Write boot header
    '''
    ret = self.write_bhdr()
    if ret != 0:
      return -1

    '''
    Write hash segment for program header
    '''
    ret = self.write_progheader_hashseg()
    if ret != 0:
      return -1

    '''
    Write hash segment for the hash table itself
    '''
    ret = self.write_itself_hashseg()
    if ret != 0:
      return -1

    '''
    Write hash segment for code segment
    '''
    ret = self.write_codeseg_hashseg()
    if ret != 0:
      return -1

    '''
    Write other hash segment
    Add code here
    '''

    '''
    Write signature & certificate
    '''
    ret = self.write_hash_certchain()
    if ret != 0:
      return -1

    '''
    Check if segment size is block aligned
    '''
    '''
    Read ELF header
    '''
    offset = 0
    self.dst_fp.seek(offset, os.SEEK_SET)
    ehdr = Elf32_Ehdr(self.dst_fp.read(ELF_HDR_SIZE))

    '''
    Read ELF hash table header
    '''
    offset = ehdr.e_phoff + ehdr.e_phentsize
    self.dst_fp.seek(offset, os.SEEK_SET)
    hashtbl_phdr = Elf32_Phdr(self.dst_fp.read(ehdr.e_phentsize))

    '''
    'if (hashtbl_phdr.p_filesz > ELF_BLOCK_ALIGN)'
    disused due to customized definition
    '''
    size = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize) + hashtbl_phdr.p_filesz
    if (size > ELF_BLOCK_ALIGN):
      off = size & (ELF_BLOCK_ALIGN - 1)
      if (int(off) != 0):
        pad = ELF_BLOCK_ALIGN - off
    else:
      pad = ELF_BLOCK_ALIGN - size

    offset = hashtbl_phdr.p_offset + hashtbl_phdr.p_filesz
    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write('\0' * pad)

    return 0

  '''
  Write boot header
  '''
  def write_bhdr(self):
    '''
    Add code here:
    image_dest_ptr
    sig_ptr
    cert_chain_ptr
    '''
    self.bhdr.image_id = ImageType.NONE_IMG
    self.bhdr.flash_parti_ver = FLASH_PARTI_VERSION
    self.bhdr.image_src = 0
    self.bhdr.image_dest_ptr = 0
    self.bhdr.code_size = self.ehdr.e_phnum * MI_PROG_BOOT_DIGEST_SIZE
    self.bhdr.image_size = self.bhdr.code_size + SHA256_SIGNATURE_SIZE + CERT_CHAIN_MAXSIZE
    self.bhdr.sig_ptr = 0
    self.bhdr.sig_size = SHA256_SIGNATURE_SIZE
    self.bhdr.cert_chain_ptr = 0
    self.bhdr.cert_chain_size = CERT_CHAIN_MAXSIZE

    values = [self.bhdr.image_id,
              self.bhdr.flash_parti_ver,
              self.bhdr.image_src,
              self.bhdr.image_dest_ptr,
              self.bhdr.image_size,
              self.bhdr.code_size,
              self.bhdr.sig_ptr,
              self.bhdr.sig_size,
              self.bhdr.cert_chain_ptr,
              self.bhdr.cert_chain_size
              ]

    packed_values = Boot_Hdr.s_part.pack(*values)

    '''
    'offset = ELF_BLOCK_ALIGN' disused due to customized definition
    '''
    offset = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize)

    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write(packed_values)

    return 0

  '''
  Write hash segment for program header
  '''
  def write_progheader_hashseg(self):
    '''
    Read ELF header
    '''
    offset = 0
    self.dst_fp.seek(offset, os.SEEK_SET)
    ehdr_buf = self.dst_fp.read(ELF_HDR_SIZE)

    '''
    Read ELF program header table
    '''
    offset = self.ehdr.e_phoff
    self.dst_fp.seek(offset, os.SEEK_SET)
    phdr_tbl_buf = self.dst_fp.read(self.ehdr.e_phnum * self.ehdr.e_phentsize)

    '''
    Generate hash
    '''
    hash = self.gen_sha1_hash(ehdr_buf + phdr_tbl_buf)

    '''
    Write hash to file as hash segment
    '''
    '''
    'offset = ELF_BLOCK_ALIGN + MI_BOOT_IMG_HDR_SIZE' disused due to customized definition
    '''
    offset = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize) + MI_BOOT_IMG_HDR_SIZE

    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write(hash)

    if len(hash) < MI_PROG_BOOT_DIGEST_SIZE:
      self.dst_fp.write('\0' * (MI_PROG_BOOT_DIGEST_SIZE - len(hash)))
    elif len(hash) > MI_PROG_BOOT_DIGEST_SIZE:
      return -1

    return 0

  '''
  Write hash segment for the hash table itself
  '''
  def write_itself_hashseg(self):
    '''
    Generate hash
    '''
    hash = '\0' * MI_PROG_BOOT_DIGEST_SIZE

    '''
    Write hash to file as hash segment
    '''
    '''
    'offset = ELF_BLOCK_ALIGN + MI_BOOT_IMG_HDR_SIZE + MI_PROG_BOOT_DIGEST_SIZE' disused due to customized definition
    '''
    offset = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize) + MI_BOOT_IMG_HDR_SIZE + MI_PROG_BOOT_DIGEST_SIZE

    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write(hash)

    return 0

  '''
  Write hash segment for code segment
  '''
  def write_codeseg_hashseg(self):
    '''
    Read ELF header
    '''
    offset = 0
    self.dst_fp.seek(offset, os.SEEK_SET)
    ehdr = Elf32_Ehdr(self.dst_fp.read(ELF_HDR_SIZE))

    '''
    Read ELF code segment header
    '''
    offset = ehdr.e_phoff + (ehdr.e_phentsize * 2)
    self.dst_fp.seek(offset, os.SEEK_SET)
    codeseg_phdr = Elf32_Phdr(self.dst_fp.read(ehdr.e_phentsize))

    '''
    Generate hash
    '''
    offset = codeseg_phdr.p_offset
    self.dst_fp.seek(offset, os.SEEK_SET)
    buf = self.dst_fp.read(codeseg_phdr.p_filesz)
    hash = self.gen_sha1_hash(buf)

    '''
    Write hash to file as hash segment
    '''
    '''
    'offset = ELF_BLOCK_ALIGN + MI_BOOT_IMG_HDR_SIZE + (MI_PROG_BOOT_DIGEST_SIZE * 2)' disused due to customized definition
    '''
    offset = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize) + MI_BOOT_IMG_HDR_SIZE + (MI_PROG_BOOT_DIGEST_SIZE * 2)

    self.dst_fp.seek(offset, os.SEEK_SET)
    self.dst_fp.write(hash)

    if len(hash) < MI_PROG_BOOT_DIGEST_SIZE:
      self.dst_fp.write('\0' * (MI_PROG_BOOT_DIGEST_SIZE - len(hash)))
    elif len(hash) > MI_PROG_BOOT_DIGEST_SIZE:
      return -1

    return 0

  '''
  Write signature & certificate
  '''
  def write_hash_certchain(self):
    '''
    Read ELF header
    '''
    offset = 0
    self.dst_fp.seek(offset, os.SEEK_SET)
    ehdr = Elf32_Ehdr(self.dst_fp.read(ELF_HDR_SIZE))

    '''
    Read ELF hash table header
    '''
    offset = ehdr.e_phoff + ehdr.e_phentsize
    self.dst_fp.seek(offset, os.SEEK_SET)
    hashtbl_phdr = Elf32_Phdr(self.dst_fp.read(ehdr.e_phentsize))

    '''
    Read data of boot header
                 + hash segment for program header
                 + hash segment for the hash table itself
                 + hash segment for code segment
                 + other hash segments
    for signature and certificate
    '''
    '''
    'offset = ELF_BLOCK_ALIGN' disused due to customized definition
    '''
    offset = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize)

    self.dst_fp.seek(offset, os.SEEK_SET)

    length = hashtbl_phdr.p_filesz - SHA256_SIGNATURE_SIZE - CERT_CHAIN_MAXSIZE
    buf = self.dst_fp.read(length)

    '''
    Create a temporary file and write data to it
    '''
    ''' disused due to the failure of access to temporary file
    ftemp = tempfile.NamedTemporaryFile()
    ftemp.write(buf)
    '''
    ftemp_name = self.namebase + '.bin'
    try:
      ftemp = open(os.path.sep.join((self.signtool, ftemp_name)), 'wb+')
    except IOError, err:
      print >> sys.stderr, str(err)
      return -1
    ftemp.write(buf)
    ftemp.close()

    '''
    Run external signature tool, and the following files are generated:

    *_attest.key
    *-signature.bin
    *-attestation_cert.cer
    *-attestation_ca_cert.cer
    *-root_cert.cer
    '''
    sign_tool = os.path.sep.join((self.signtool, 'QDST.py'))
    hashseg_file = 'image=' + ftemp_name
    config_file = 'xml=' + 'QDST_' + self.namebase + '.xml'
    cmd = ['python', sign_tool, hashseg_file, config_file]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out = proc.communicate()[0]

    '''
    print >> sys.stdout, out
    '''

    if proc.returncode != 0:
      return -1

    '''
    Write signature and certificate into ELF, as the followings:

    *-signature.bin
    *-attestation_cert.cer
    *-attestation_ca_cert.cer
    *-root_cert.cer
    '''
    try:
      zipname = 'cert/' + 'QDST_Qualcomm_' + self.namebase + '.zip'
      dirname = 'cert'
      self.unzip(os.path.sep.join((self.signtool, zipname)), os.path.sep.join((self.signtool, dirname)))
    except err:
      print >> sys.stderr, str(err)
      return -1

    '''
    'offset = ELF_BLOCK_ALIGN + hashtbl_phdr.p_filesz - SHA256_SIGNATURE_SIZE - CERT_CHAIN_MAXSIZE'
    disused due to customized definition
    '''
    offset = self.ehdr.e_phoff + (self.ehdr.e_phnum * self.ehdr.e_phentsize) + \
        hashtbl_phdr.p_filesz - SHA256_SIGNATURE_SIZE - CERT_CHAIN_MAXSIZE

    self.dst_fp.seek(offset, os.SEEK_SET)

    for root, dirs, files in os.walk(os.path.sep.join((self.signtool, dirname))):
      for name in files:
        if name == 'QDST_Qualcomm_' + self.namebase + '-signature.bin':
          try:
            fp_read = open(os.path.sep.join((self.signtool, dirname, name)), 'rb')
          except IOError, err:
            print >> sys.stderr, str(err)
            return -1

          length = os.stat(os.path.sep.join((self.signtool, dirname, name))).st_size

          buf = fp_read.read(length)
          self.dst_fp.write(str(buf))
          fp_read.close()

          '''
          Check if signature is size aligned
          '''
          if length > SHA256_SIGNATURE_SIZE:
            off = length & (SHA256_SIGNATURE_SIZE - 1)
            if (int(off) != 0):
              pad = SHA256_SIGNATURE_SIZE - off
          else:
            pad = SHA256_SIGNATURE_SIZE - length

          self.dst_fp.seek(offset + length, os.SEEK_SET)
          self.dst_fp.write('\0' * pad)

          break

      len_certchain = 0

      for name in files:
        if name == 'QDST_Qualcomm_' + self.namebase + '-attestation_cert.cer':
          try:
            fp_read = open(os.path.sep.join((self.signtool, dirname, name)), 'rb')
          except IOError, err:
            print >> sys.stderr, str(err)
            return -1

          length = os.stat(os.path.sep.join((self.signtool, dirname, name))).st_size

          buf = fp_read.read(length)
          self.dst_fp.write(str(buf))
          fp_read.close()

          len_certchain += length

          break

      for name in files:
        if name == 'QDST_Qualcomm_' + self.namebase + '-attestation_ca_cert.cer':
          try:
            fp_read = open(os.path.sep.join((self.signtool, dirname, name)), 'rb')
          except IOError, err:
            print >> sys.stderr, str(err)
            return -1

          length = os.stat(os.path.sep.join((self.signtool, dirname, name))).st_size

          buf = fp_read.read(length)
          self.dst_fp.write(str(buf))
          fp_read.close()

          len_certchain += length
          break

      for name in files:
        if name == 'QDST_Qualcomm_' + self.namebase + '-root_cert.cer':
          try:
            fp_read = open(os.path.sep.join((self.signtool, dirname, name)), 'rb')
          except IOError, err:
            print >> sys.stderr, str(err)
            return -1

          length = os.stat(os.path.sep.join((self.signtool, dirname, name))).st_size

          buf = fp_read.read(length)
          self.dst_fp.write(str(buf))
          fp_read.close()

          len_certchain += length
          break

      break

    '''
    Check if certificate chain is size aligned
    '''
    if len_certchain > CERT_CHAIN_MAXSIZE:
      off = len_certchain & (CERT_CHAIN_MAXSIZE - 1)
      if (int(off) != 0):
        pad = CERT_CHAIN_MAXSIZE - off
    else:
      pad = CERT_CHAIN_MAXSIZE - len_certchain

    self.dst_fp.seek(offset + SHA256_SIGNATURE_SIZE + len_certchain, os.SEEK_SET)
    self.dst_fp.write(chr(0xFF) * pad)

    '''
    Clean up the following files:

    *_attest.key
    *-signature.bin
    *-attestation_cert.cer
    *-attestation_ca_cert.cer
    *-root_cert.cer
    temporary file
    '''
    '''
    Add code here
    '''

    return 0

  '''
  Write code segment
  '''
  def write_code_seg(self):
    '''
    Read ELF header
    '''
    offset = 0
    self.dst_fp.seek(offset, os.SEEK_SET)
    ehdr = Elf32_Ehdr(self.dst_fp.read(ELF_HDR_SIZE))

    '''
    Read ELF code segment header
    '''
    offset = ehdr.e_phoff + (ehdr.e_phentsize * 2)
    self.dst_fp.seek(offset, os.SEEK_SET)
    codeseg_phdr = Elf32_Phdr(self.dst_fp.read(ehdr.e_phentsize))

    '''
    Write code to file as code segment
    '''
    offset = codeseg_phdr.p_offset
    self.dst_fp.seek(offset, os.SEEK_SET)

    try:
      buf = self.src_fp.read(self.src_sz)
      self.dst_fp.write(str(buf))
    except IOError, err:
      print >> sys.stderr, str(err)
      return -1

    '''
    Check if segment size is block aligned
    '''
    if codeseg_phdr.p_filesz > ELF_BLOCK_ALIGN:
      off = codeseg_phdr.p_filesz & (ELF_BLOCK_ALIGN - 1)
      if (int(off) != 0):
        pad = ELF_BLOCK_ALIGN - off
    else:
      pad = ELF_BLOCK_ALIGN - codeseg_phdr.p_filesz

    self.dst_fp.write('\0' * pad)

    return 0

  '''
  Build ELF file
  '''
  def build(self):
    '''
    Write ELF header
    '''
    '''
    Add code here
    entry
    '''
    entry = 0
    phnum = 3

    ret = self.write_exec_ehdr(entry, phnum)
    if ret != 0:
      raise os.error

    '''
    Write ELF program header table
    '''
    ret = self.write_phdr_tbl()
    if ret != 0:
      raise os.error

    '''
    Write Hash table
    Do nothing here
    '''

    '''
    Write code segment
    '''
    ret = self.write_code_seg()
    if ret != 0:
      raise os.error

    '''
    Write other segments
    Add code here
    '''

  '''
  Flush content of file to disk
  '''
  def flush(self):
    '''
    Write Hash table
    Recalculate hash and rewrite hash table required
    '''
    ret = self.write_hash_tbl()
    if ret != 0:
      raise os.error

'''
Build Auth-Sec ELF
'''
def build_auth_sec_elf(directory, signtool = None, namebase = None):
  ft = filetype_table['ko'][1]

  for dir, dirs, files in os.walk(directory):
    for f in files:
      try:
        if f.rfind(ft) != -1 and f[f.rfind(ft):] == ft:
          fname = os.path.sep.join((dir, f))
          if S_ISREG(os.stat(fname).st_mode):
            ElfBuilder(fname, fname + '.sec', signtool, namebase)
            '''
            Remove original file
            Add code here
            '''
      except os.error, err:
        '''
        Ignore error due to unrecognized file
        '''
        print >> sys.stderr, str(err).replace('Errno', 'Warning')

  return 0

'''
Print Usage
'''
def print_usage():
    print >> sys.stdout, 'USAGE: python elfimg-tool.py [OPTION...]'
    print >> sys.stdout, ''
    print >> sys.stdout, 'OPTIONS:'
    print >> sys.stdout, '  -d, --dir        Directory to generate ELF file'
    print >> sys.stdout, '  -s, --sign       Directory of signature tool to sign ELF file'
    print >> sys.stdout, '  -b, --base       Base name of signature and certificate chain'
    print >> sys.stdout, '  -h, --help       Display help message'
    print >> sys.stdout, ''

'''
Main Entry
'''
def main():
  directory = ''
  signtool = ''
  basename = ''
  ret = 0

  '''
  Display banner
  '''
  print(banner)

  '''
  Get args list
  '''
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:s:b:h', ['dir', 'sign', 'base', 'help'])
  except getopt.GetoptError, err:
    print >> sys.stderr, err
    print_usage()
    sys.exit(1)

  for o, a in opts:
    if o in ('-d', '--dir'):
      directory = a
    elif o in ('-s', '--sign'):
      signtool = a
    elif o in ('-b', '--base'):
      basename = a
    elif o in ('-h', '--help'):
      print_usage()
      sys.exit(0)
    else:
      continue

  '''
  Sanity check
  '''
  if len(directory) == 0 or os.access(directory, os.F_OK | os.R_OK) is False:
    print >> sys.stderr, 'error: failed to open directory!'
    exit(1)

  if len(signtool) == 0 or os.access(signtool, os.F_OK | os.R_OK | os.X_OK) is False:
    print >> sys.stderr, 'error: failed to access signature tool!'
    exit(1)

  if len(basename) == 0:
    print >> sys.stderr, 'error: invalid base name!'
    exit(1)

  '''
  Build auth-sec ELF with signature and certificate chain
  '''
  ret = build_auth_sec_elf(directory, signtool, basename)
  if ret != 0:
    print >> sys.stderr, 'error: failed to build auth-sec ELF file!'
    exit(1)

  print >> sys.stdout, 'done.'

if __name__ == '__main__':
  main()
