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
import math

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
EXT4_BLOCK_SZ       = 4096
EXT4_MIN_BLOCK_SIZE = 1024
EXT4_MAX_BLOCK_SIZE = 65536

EXT4_GROUP_0_PAD_LEN = 1024

EXT4_SUPER_MAGIC = 0xEF53

EXT4_JNL_BACKUP_BLOCKS = 1

EXT4_STATE = {
    'EXT4_VALID_FS'  : 0x0001,
    'EXT4_ERROR_FS'  : 0x0002,
    'EXT4_ORPHAN_FS' : 0x0004
}

EXT4_ERRORS = {
    'EXT4_ERRORS_CONTINUE' : 1,
    'EXT4_ERRORS_RO'       : 2,
    'EXT4_ERRORS_PANIC'    : 3
}

EXT4_OS = {
    'EXT4_OS_LINUX'   : 0,
    'EXT4_OS_HURD'    : 1,
    'EXT4_OS_MASIX'   : 2,
    'EXT4_OS_FREEBSD' : 3,
    'EXT4_OS_LITES'   : 4
}

EXT4_REV_LEVEL = {
    'EXT4_GOOD_OLD_REV' : 0,
    'EXT4_DYNAMIC_REV'  : 1
}

EXT4_DEF_RESERVED_ID = {
    'EXT4_DEF_RESUID' : 0,
    'EXT4_DEF_RESGID' : 0
}

EXT4_INODE_NO = {
    'EXT4_BAD_INO'            : 1,
    'EXT4_ROOT_INO'           : 2,
    'EXT4_BOOT_LOADER_INO'    : 5 , 
    'EXT4_UNDEL_DIR_INO'      : 6,
    'EXT4_RESIZE_INO'         : 7,
    'EXT4_JOURNAL_INO'        : 8,
    'EXT4_GOOD_OLD_FIRST_INO' : 11
}

EXT4_FEATURE_COMPAT = {
    'EXT4_FEATURE_COMPAT_DIR_PREALLOC'  : 0x0001,
    'EXT4_FEATURE_COMPAT_IMAGIC_INODES' : 0x0002,
    'EXT4_FEATURE_COMPAT_HAS_JOURNAL'   : 0x0004,
    'EXT4_FEATURE_COMPAT_EXT_ATTR'      : 0x0008,
    'EXT4_FEATURE_COMPAT_RESIZE_INODE'  : 0x0010,
    'EXT4_FEATURE_COMPAT_DIR_INDEX'     : 0x0020
}

EXT4_FEATURE_INCOMPAT = {
    'EXT4_FEATURE_INCOMPAT_COMPRESSION' : 0x0001,
    'EXT4_FEATURE_INCOMPAT_FILETYPE'    : 0x0002,
    'EXT4_FEATURE_INCOMPAT_RECOVER'     : 0x0004,
    'EXT4_FEATURE_INCOMPAT_JOURNAL_DEV' : 0x0008,
    'EXT4_FEATURE_INCOMPAT_META_BG'     : 0x0010,
    'EXT4_FEATURE_INCOMPAT_EXTENTS'     : 0x0040,
    'EXT4_FEATURE_INCOMPAT_64BIT'       : 0x0080,
    'EXT4_FEATURE_INCOMPAT_MMP'         : 0x0100,
    'EXT4_FEATURE_INCOMPAT_FLEX_BG'     : 0x0200,
    'EXT4_FEATURE_INCOMPAT_EA_INODE'    : 0x0400,
    'EXT4_FEATURE_INCOMPAT_DIRDATA'     : 0x1000
}

EXT4_FEATURE_RO_COMPAT = {
    'EXT4_FEATURE_RO_COMPAT_SPARSE_SUPER' : 0x0001,
    'EXT4_FEATURE_RO_COMPAT_LARGE_FILE'   : 0x0002,
    'EXT4_FEATURE_RO_COMPAT_BTREE_DIR'    : 0x0004,
    'EXT4_FEATURE_RO_COMPAT_HUGE_FILE'    : 0x0008,
    'EXT4_FEATURE_RO_COMPAT_GDT_CSUM'     : 0x0010,
    'EXT4_FEATURE_RO_COMPAT_DIR_NLINK'    : 0x0020,
    'EXT4_FEATURE_RO_COMPAT_EXTRA_ISIZE'  : 0x0040
}

EXT4_HASH_VER = {
    'DX_HASH_LEGACY'            : 0,
    'DX_HASH_HALF_MD4'          : 1,
    'DX_HASH_TEA'               : 2,
    'DX_HASH_LEGACY_UNSIGNED'   : 3,
    'DX_HASH_HALF_MD4_UNSIGNED' : 4,
    'DX_HASH_TEA_UNSIGNED'      : 5
}

EXT4_DEFAULT_MOUNT_OPTS = {
    'EXT2_DEFM_DEBUG'          : 0x0001,
    'EXT2_DEFM_BSDGROUPS'      : 0x0002,
    'EXT2_DEFM_XATTR_USER'     : 0x0004,
    'EXT2_DEFM_ACL'            : 0x0008,
    'EXT2_DEFM_UID16'          : 0x0010,
    'EXT3_DEFM_JMODE_DATA'     : 0x0020,
    'EXT3_DEFM_JMODE_ORDERED'  : 0x0040,
    'EXT3_DEFM_JMODE'          : 0x0060,
    'EXT3_DEFM_JMODE_WBACK'    : 0x0060,
    'EXT4_DEFM_NOBARRIER'      : 0x0100,
    'EXT4_DEFM_BLOCK_VALIDITY' : 0x0200,
    'EXT4_DEFM_DISCARD'        : 0x0400,
    'EXT4_DEFM_NODELALLOC'     : 0x0800
}

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
        # Ext4 block size
        #
        self.ext4_block_sz = EXT4_BLOCK_SZ

        #
        # Ext4 super block
        #
        self.ext4_super_block = {
            's_inodes_count'         : 0,  # Total inode count, le32
            's_blocks_count_lo'      : 0,  # Total block count, le32
            's_r_blocks_count_lo'    : 0,  # Reserved block count, le32
            's_free_blocks_count_lo' : 0,  # Free block count, le32
            's_free_inodes_count'    : 0,  # Free inode count, le32
            's_first_data_block'     : 0,  # First data block, le32
            's_log_block_size'       : 0,  # Block size is 2 ^ (10 + s_log_block_size), le32
            's_obso_log_frag_size'   : 0,  # (Obsolete) fragment size, le32
            's_blocks_per_group'     : 0,  # Blocks per group, le32
            's_obso_frags_per_group' : 0,  # (Obsolete) fragments per group, le32
            's_inodes_per_group'     : 0,  # Inodes per group, le32
            's_mtime'                : 0,  # Mount time, in seconds since the epoch, le32
            's_wtime'                : 0,  # Write time, in seconds since the epoch, le32
            's_mnt_count'            : 0,  # Number of mounts since the last fsck, le16
            's_max_mnt_count'        : 0xFFFF,  # Number of mounts beyond which a fsck is needed, le16
            's_magic'                : EXT4_SUPER_MAGIC,  # Magic signature, le16
            's_state'                : EXT4_STATE['EXT4_VALID_FS'],  # File system stat, le16
            's_errors'               : EXT4_ERRORS['EXT4_ERRORS_RO'],  # Behaviour when detecting errors, le16
            's_minor_rev_level'      : 0,  # Minor revision level, le16
            's_lastcheck'            : 0,  # Time of last check, in seconds since the epoch, le32
            's_checkinterval'        : 0,  # Maximum time between checks, in seconds, le32
            's_creator_os'           : EXT4_OS['EXT4_OS_LINUX'],  # OS, le32
            's_rev_level'            : EXT4_REV_LEVEL['EXT4_DYNAMIC_REV'],  # Revision level, le32
            's_def_resuid'           : EXT4_DEF_RESERVED_ID['EXT4_DEF_RESUID'],  # Default uid for reserved blocks, le16
            's_def_resgid'           : EXT4_DEF_RESERVED_ID['EXT4_DEF_RESGID'],  # Default gid for reserved blocks, le16

            #
            # These fields are for EXT4_DYNAMIC_REV superblocks only
            #
            's_first_ino'              : EXT4_INODE_NO['EXT4_GOOD_OLD_FIRST_INO'],  # First non-reserved inode, le32
            's_inode_size'             : 0,  # Size of inode structure, in bytes, le16
            's_block_group_nr'         : 0,  # Block group # of this superblock, le16
            's_feature_compat'         : 0,  # Compatible feature set flags, le32
            's_feature_incompat'       : 0,  # Incompatible feature set, le32
            's_feature_ro_compat'      : 0,  # Readonly-compatible feature set, le32
            's_uuid'                   : 0,  # 128-bit UUID for volume, u8[16]
            's_volume_name'            : "", # Volume label, char[16]
            's_last_mounted'           : "", # Directory where filesystem was last mounted, char[64]
            's_algorithm_usage_bitmap' : 0,  # For compression, le32

            #
            # Performance hints
            # Directory preallocation should only happen 
            # if the EXT4_FEATURE_COMPAT_DIR_PREALLOC flag is on
            #
            's_prealloc_blocks'     : 0,  # # of blocks to try to preallocate for files, u8
            's_prealloc_dir_blocks' : 0,  # # of blocks to preallocate for directories, u8
            's_reserved_gdt_blocks' : 0,  # number of reserved GDT entries for future filesystem expansion, le16

            #
            # Journaling support valid if EXT4_FEATURE_COMPAT_HAS_JOURNAL set
            #
            's_journal_uuid'       : 0,  # UUID of journal superblock, u8[16]
            's_journal_inum'       : EXT4_INODE_NO['EXT4_JOURNAL_INO'],  # inode number of journal file, le32
            's_journal_dev'        : 0,  # Device number of journal file, if the external journal feature flag is set, le32
            's_last_orphan'        : 0,  # Start of list of orphaned inodes to delete, le32
            's_hash_seed'          : 0,  # HTREE hash seed, le32[4]
            's_def_hash_version'   : EXT4_HASH_VER['DX_HASH_TEA'],  # Default hash algorithm to use for directory hashes, u8
            's_reserved_char_pad'  : EXT4_JNL_BACKUP_BLOCKS,  # Reserved char padding, u8
            's_desc_size'          : 0, # Size of group descriptors, in bytes, if the 64bit incompat feature flag is set, le16
            's_default_mount_opts' : 0x0000,  # Default mount options, le32
            's_first_meta_bg'      : 0,  # First metablock block group, if the meta_bg feature is enabled, le32
            's_mkfs_time'          : 0,  # When the filesystem was created, in seconds since the epoch, le32
            's_jnl_blocks'         : 0,  # Backup copy of the first 68 bytes of the journal inode, le32[17]

            #
            # 64bit support valid if EXT4_FEATURE_COMPAT_64BIT
            # 
            's_blocks_count_hi'      : 0,  # High 32-bits of the block count, le32
            's_r_blocks_count_hi'    : 0,  # High 32-bits of the reserved block count, le32
            's_free_blocks_count_hi' : 0,  # High 32-bits of the free block count, le32
            's_min_extra_isize'      : 0,  # All inodes have at least # bytes, le16
            's_want_extra_isize'     : 0,  # New inodes should reserve # bytes, le16
            's_flags'                : 0x0000,  # Miscellaneous flags, le32
            's_raid_stride'          : 0,  # RAID stride. This is the number of logical blocks read
                                           # from or written to the disk before moving to the next
                                           # disk. This affects the placement of filesystem metadata,
                                           # which will hopefully make RAID storage faster, le16
            's_mmp_interval'         : 0,  # # seconds to wait in multi-mount prevention (MMP) checking.
                                           # In theory, MMP is a mechanism to record in the superblock
                                           # which host and device have mounted the filesystem, in
                                           # order to prevent multiple mounts. This feature does not
                                           # seem to be implemented, le16
            's_mmp_block'            : 0,  # Block # for multi-mount protection data, le64
            's_raid_stripe_width'    : 0,  # RAID stripe width. This is the number of logical
                                           # blocks read from or written to the disk before
                                           # coming back to the current disk. This is used by 
                                           # the block allocator to try to reduce the number
                                           # of read-modify-write operations in a RAID5/6, le32
            's_log_groups_per_flex'  : 0,  # Size of a flexible block group is 2 ^ s_log_groups_per_flex, u8
            's_reserved_char_pad2'   : 0,  # Reserved char padding 2, u8
            's_reserved_pad'         : 0,  # Reserved padding, le16
            's_kbytes_written'       : 0,  # Number of KiB written to this filesystem over its lifetime, le64
            's_reserved'             : 0,  # Reserved, u32[160];
}

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
        return True

    #
    # Parse Ext4 super block
    #
    def parse_ext4_sb(self, offset):
        self.ext4_super_block['s_inodes_count'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_blocks_count_lo'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_r_blocks_count_lo'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_free_blocks_count_lo'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_free_inodes_count'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_first_data_block'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_log_block_size'] = self.str2int(self.image[offset:offset+4])
        self.ext4_block_sz = int(math.pow(2, (10 + self.ext4_super_block['s_log_block_size'])))

        offset += 4
        self.ext4_super_block['s_obso_log_frag_size'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_blocks_per_group'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_obso_frags_per_group'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_inodes_per_group'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_mtime'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_wtime'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_mnt_count'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_max_mnt_count'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_magic'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_state'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_errors'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_minor_rev_level'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_lastcheck'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_checkinterval'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_creator_os'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_rev_level'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_def_resuid'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_def_resgid'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_first_ino'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_inode_size'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_block_group_nr'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_feature_compat'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_feature_incompat'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_feature_ro_compat'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_uuid'] = self.str2int(self.image[offset:offset+16])

        offset += 16
        self.ext4_super_block['s_volume_name'] = self.image[offset:offset+16]

        offset += 16
        self.ext4_super_block['s_last_mounted'] = self.image[offset:offset+64]

        offset += 64
        self.ext4_super_block['s_algorithm_usage_bitmap'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_prealloc_blocks'] = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_prealloc_dir_blocks'] = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_reserved_gdt_blocks'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_journal_uuid'] = self.str2int(self.image[offset:offset+16])

        offset += 16
        self.ext4_super_block['s_journal_inum'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_journal_dev'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_last_orphan'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_hash_seed'] = self.str2int(self.image[offset:offset+16])

        offset += 16
        self.ext4_super_block['s_def_hash_version'] = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_reserved_char_pad'] = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_desc_size'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_default_mount_opts'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_first_meta_bg'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_mkfs_time'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_jnl_blocks'] = self.str2int(self.image[offset:offset+68])

    #
    # Print Ext4 super block info
    #
    def print_ext4_sb_info(self):
        print("----------------------------------------")
        print("Ext4 SUPER BLOCK INFO\n")

        print("Total inode count : " + str(self.ext4_super_block['s_inodes_count']))
        print("Total block count : " + str((self.ext4_super_block['s_blocks_count_hi'] << 32) + self.ext4_super_block['s_blocks_count_lo']))
        print("Reserved block count : " + str((self.ext4_super_block['s_r_blocks_count_hi'] << 32) + self.ext4_super_block['s_r_blocks_count_lo']))
        print("Free block count : " + str((self.ext4_super_block['s_free_blocks_count_hi'] << 32) + self.ext4_super_block['s_free_blocks_count_lo']))
        print("Free inode count : " + str(self.ext4_super_block['s_free_inodes_count']))
        print("First data block : " + str(self.ext4_super_block['s_first_data_block']))
        print("Block size: " + str(self.ext4_block_sz))
        print("Fragment size (obsolete) : " + str(int(math.pow(2, (10 + self.ext4_super_block['s_obso_log_frag_size'])))))
        print("Blocks per group : " + str(self.ext4_super_block['s_blocks_per_group']))
        print("Fragments per group (obsolete): " + str(self.ext4_super_block['s_obso_frags_per_group']))
        print("Inodes per group: " + str(self.ext4_super_block['s_inodes_per_group']))
        print("Mount time (seconds): " + str(self.ext4_super_block['s_mtime']))
        print("Write time (seconds): " + str(self.ext4_super_block['s_wtime']))
        print("Mount count: " + str(self.ext4_super_block['s_mnt_count']))
        print("Maximum mount count: " + str(self.ext4_super_block['s_max_mnt_count']))
        print("Magic signature: 0x%X" % self.ext4_super_block['s_magic'])

        for k, v in EXT4_STATE.items():
            if v == self.ext4_super_block['s_state']:
                print("File system state: " + k)

        for k, v in EXT4_ERRORS.items():
            if v == self.ext4_super_block['s_errors']:
                print("Errors behaviour: " + k)

        print("Minor revision level: " + str(self.ext4_super_block['s_minor_rev_level']))
        print("Last checked: " + str(self.ext4_super_block['s_lastcheck']))
        print("Check interval: " + str(self.ext4_super_block['s_checkinterval']))

        for k, v in EXT4_OS.items():
            if v == self.ext4_super_block['s_creator_os']:
                print("OS type: " + k)

        for k, v in EXT4_REV_LEVEL.items():
            if v == self.ext4_super_block['s_rev_level']:
                print("Revision level: " + k)

        print("Reserved blocks uid: " + str(self.ext4_super_block['s_def_resuid']))
        print("Reserved blocks gid: " + str(self.ext4_super_block['s_def_resgid']))
        print("First non-reserved inode: " + str(self.ext4_super_block['s_first_ino']))
        print("Inode size: " + str(self.ext4_super_block['s_inode_size']))
        print("Block group number: " + str(self.ext4_super_block['s_block_group_nr']))

        feature_compat = ""
        for k, v in EXT4_FEATURE_COMPAT.items():
            if (v & self.ext4_super_block['s_feature_compat']) != 0:
                feature_compat += " " + k
        print("Compatible feature: " + feature_compat)

        feature_incompat = ""
        for k, v in EXT4_FEATURE_INCOMPAT.items():
            if (v & self.ext4_super_block['s_feature_incompat']) != 0:
                feature_incompat += " " + k
        print("Incompatible feature: " + feature_incompat)

        feature_ro_compat = ""
        for k, v in EXT4_FEATURE_RO_COMPAT.items():
            if (v & self.ext4_super_block['s_feature_ro_compat']) != 0:
                feature_ro_compat += " " + k
        print("Readonly-compatible feature: " + feature_ro_compat)

        print("UUID: %x" % self.ext4_super_block['s_uuid'])
        print("Volume name: " + self.ext4_super_block['s_volume_name'])
        print("Last mounted on: " + self.ext4_super_block['s_last_mounted'])
        print("Bitmap algorithm usage: " + str(self.ext4_super_block['s_algorithm_usage_bitmap']))
        print("Blocks preallocated for files: " + str(self.ext4_super_block['s_prealloc_blocks']))
        print("Blocks preallocated for dirs: " + str(self.ext4_super_block['s_prealloc_dir_blocks']))
        print("Reserved GDT blocks: " + str(self.ext4_super_block['s_reserved_gdt_blocks']))
        print("Journal UUID: %x" % self.ext4_super_block['s_journal_uuid'])
        print("Journal inode: " + str(self.ext4_super_block['s_journal_inum']))
        print("Journal device: " + str(self.ext4_super_block['s_journal_dev']))
        print("Orphaned inodes to delete: " + str(self.ext4_super_block['s_last_orphan']))
        print("HTREE hash seed: %x" % self.ext4_super_block['s_hash_seed'])
        print("Default hash version for dirs hashes: " + str(self.ext4_super_block['s_def_hash_version']))
        print("Reserved char padding: " + str(self.ext4_super_block['s_reserved_char_pad']))
        print("Group descriptors size: " + str(self.ext4_super_block['s_desc_size']))

        default_mount_opts = ""
        for k, v in EXT4_DEFAULT_MOUNT_OPTS.items():
            if (v & self.ext4_super_block['s_default_mount_opts']) != 0:
                default_mount_opts  += " " + k
        print("Default mount options: " + default_mount_opts)
        print("First metablock block group: " + str(self.ext4_super_block['s_first_meta_bg']))
        print("Filesystem-created time (seconds): " + str(self.ext4_super_block['s_mkfs_time']))
        print("Journal backup: %x" % self.ext4_super_block['s_jnl_blocks'])

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
        # Parse Ext4 super block
        #
        offset = EXT4_GROUP_0_PAD_LEN
        self.parse_ext4_sb(offset)

        #
        # Print Ext4 super block info
        #
        if is_pr_verb is True:
            self.print_ext4_sb_info()

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
