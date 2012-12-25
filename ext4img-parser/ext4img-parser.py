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

EXT4_GROUP_0_PAD_SZ = 1024

EXT4_SUPER_MAGIC = 0xEF53

EXT4_JNL_BACKUP_BLOCKS = 1

EXT4_NDIR_BLOCKS = 12
EXT4_IND_BLOCK   = EXT4_NDIR_BLOCKS
EXT4_DIND_BLOCK  = EXT4_IND_BLOCK + 1
EXT4_TIND_BLOCK  = EXT4_DIND_BLOCK + 1
EXT4_N_BLOCKS    = EXT4_TIND_BLOCK + 1

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
    'EXT4_BOOT_LOADER_INO'    : 5,
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

EXT4_DEFAULT_HASH_VER = {
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

EXT4_MISC_FLAGS = {
    'EXT2_FLAGS_SIGNED_HASH'   : 0x0001,
    'EXT2_FLAGS_UNSIGNED_HASH' : 0x0002,
    'EXT2_FLAGS_TEST_FILESYS'  : 0x0004,
    'EXT2_FLAGS_IS_SNAPSHOT'   : 0x0010,
    'EXT2_FLAGS_FIX_SNAPSHOT'  : 0x0020,
    'EXT2_FLAGS_FIX_EXCLUDE'   : 0x0040
}

EXT4_BG_FLAGS = {
    'EXT2_BG_INODE_UNINIT' : 0x0001,
    'EXT2_BG_BLOCK_UNINIT' : 0x0002,
    'EXT2_BG_INODE_ZEROED' : 0x0004
}

EXT4_INODE_MODE = {
    'S_IXOTH' : 0x1,
    'S_IWOTH' : 0x2,
    'S_IROTH' : 0x4,
    'S_IXGRP' : 0x8,
    'S_IWGRP' : 0x10,
    'S_IRGRP' : 0x20,
    'S_IXUSR' : 0x40,
    'S_IWUSR' : 0x80,
    'S_IRUSR' : 0x100,
    'S_ISVTX' : 0x200,
    'S_ISGID' : 0x400,
    'S_ISUID' : 0x800,
    
    #
    # These are mutually-exclusive file types
    #
    'S_IFIFO'  : 0x1000,
    'S_IFCHR'  : 0x2000,
    'S_IFDIR'  : 0x4000,
    'S_IFBLK'  : 0x6000,
    'S_IFREG'  : 0x8000,
    'S_IFLNK'  : 0xA000,
    'S_IFSOCK' : 0xC000
}

EXT4_INODE_FLAGS = {
    'FILE_SEC_DEL'                   : 0x1,  # This file requires secure deletion. (not implemented)
    'FILE_UNDEL'                     : 0x2,  # This file should be preserved should undeletion be desired. (not implemented)
    'FILE_COMPRESSED'                : 0x4,  # File is compressed. (not really implemented)
    'FILE_WRITE_SYNC'                : 0x8,  # All writes to the file must be synchronous.
    'FILE_IMMUTABLE'                 : 0x10,  # File is immutable.
    'FILE_APPENDED_ONLY'             : 0x20,  # File can only be appended.
    'FILE_NOT_DUMPED'                : 0x40,  # The dump utility should not dump this file.
    'FILE_NOT_UPDATE_ATIME'          : 0x80,  # Do not update access time.
    'FILE_DIRTY_COMPRESSED'          : 0x100,  # Dirty compressed file. (not used)
    'FILE_COMPRESSED_CLUSTERS'       : 0x200,  # File has one or more compressed clusters. (not used)
    'FILE_NOT_COMPRESSED'            : 0x400,  # Do not compress file. (not used)
    'FILE_COMPRESS_ERR'              : 0x800,  # Compression error. (not used)
    'DIR_HASHED_INDEXES'             : 0x1000,  # Directory has hashed indexes.
    'DIR_AFS_MAGIC'                  : 0x2000,  # AFS magic directory.
    'FILE_WRITE_THROUGH_JNL'         : 0x4000,  # File data must always be written through the journal.
    'FILE_TAIL_NOT_MERGED'           : 0x8000,  # File tail should not be merged.
    'DIR_WRITE_SYNC'                 : 0x10000,  # All directory entry data should be written synchronously (see dirsync).
    'DIR_TOP_HIERARCHY'              : 0x20000,  # Top of directory hierarchy.
    'FILE_HUGE'                      : 0x40000,  # This is a huge file.
    'INODE_USE_EXTENTS'              : 0x80000,  # Inode uses extents.
    'INODE_USE_LARGE_EXTEND_ATTR'    : 0x200000,  # Inode used for a large extended attribute.
    'FILE_BLOCKS_ALLOCATED_PAST_EOF' : 0x400000,  # This file has blocks allocated past EOF.
    'RESERVED_EXT4_LIB'              : 0x80000000,  # Reserved for ext4 library.

    #
    # Aggregate flags
    #
    'USER_VISIBLE'    : 0x4BDFFF,  # User-visible flags.
    'USER_MODIFIABLE' : 0x4B80FF,  # User-modifiable flags. 
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
            's_def_hash_version'   : EXT4_DEFAULT_HASH_VER['DX_HASH_TEA'],  # Default hash algorithm to use for directory hashes, u8
            's_reserved_char_pad'  : EXT4_JNL_BACKUP_BLOCKS,  # Reserved char padding, u8
            's_desc_size'          : 0, # Size of group descriptors, in bytes, if the 64bit incompat feature flag is set, le16
            's_default_mount_opts' : 0x0000,  # Default mount options, le32
            's_first_meta_bg'      : 0,  # First metablock block group, if the meta_bg feature is enabled, le32
            's_mkfs_time'          : 0,  # When the filesystem was created, in seconds since the epoch, le32
            's_jnl_blocks'         : 0,  # Backup copy of the first 68 bytes of the journal inode, le32[17]

            #
            # 64bit support valid if EXT4_FEATURE_INCOMPAT_64BIT
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
        # Ext4 block group descriptor
        #
        self.ext4_block_group_desc = {
            'bg_block_bitmap_lo'      : 0,  # Lower 32-bits of location of block bitmap, le32
            'bg_inode_bitmap_lo'      : 0,  # Lower 32-bits of location of inode bitmap, le32
            'bg_inode_table_lo'       : 0,  # Lower 32-bits of location of inode table, le32
            'bg_free_blocks_count_lo' : 0,  # Lower 16-bits of free block count, le16
            'bg_free_inodes_count_lo' : 0,  # Lower 16-bits of free inode count, le16
            'bg_used_dirs_count_lo'   : 0,  # Lower 16-bits of directory count, le16
            'bg_flags'                : EXT4_BG_FLAGS['EXT2_BG_INODE_UNINIT'],  # Block group flags, le16
            'bg_exclude_bitmap_lo'    : 0,  # Lower 32-bits of location of exclusion bitmap, le32
            'bg_reserved1'            : 0,  # Inode bitmap checksum, u32
            'bg_itable_unused_lo'     : 0,  # Lower 16-bits of unused inode count, le16
            'bg_checksum'             : 0,  # Group descriptor checksum, le16

            #
            # 64bit support valid if EXT4_FEATURE_INCOMPAT_64BIT and 's_desc_size' > 32
            #
            'bg_block_bitmap_hi'      : 0,  # Upper 32-bits of location of block bitmap, le32
            'bg_inode_bitmap_hi'      : 0,  # Upper 32-bits of location of inodes bitmap, le32
            'bg_inode_table_hi'       : 0,  # Upper 32-bits of location of inodes table, le32
            'bg_free_blocks_count_hi' : 0,  # Upper 16-bits of free block count, le16
            'bg_free_inodes_count_hi' : 0,  # Upper 16-bits of free inode count, le16
            'bg_used_dirs_count_hi'   : 0,  # Upper 16-bits of directory count, le16
            'bg_itable_unused_hi'     : 0,  # Upper 16-bits of unused inode count, le16
            'bg_exclude_bitmap_hi'    : 0,  # Upper 32-bits of location of exclusion bitmap, le32
            'bg_reserved2'            : 0,  # Block bitmap checksum, u32
            'bg_reserved3'            : 0,  # Padding to 64 bytes, u32[2]
            }

        #
        # Ext4 inode table
        #
        self.ext4_inode_table = {
            'i_mode'            : EXT4_INODE_MODE['S_IXOTH'],  # File mode, le16
            'i_uid'             : 0,  # Lower 16-bits of Owner UID, le16
            'i_size_lo'         : 0,  # Lower 32-bits of size in bytes, le32
            'i_atime'           : 0,  # Last access time, in seconds since the epoch, le32
            'i_ctime'           : 0,  # Last inode change time, in seconds since the epoch, le32
            'i_mtime'           : 0,  # Last data modification time, in seconds since the epoch, le32
            'i_dtime'           : 0,  # Deletion Time, in seconds since the epoch, le32
            'i_gid'             : 0,  # Lower 16-bits of GID, le16
            'i_links_count'     : 0,  # Hard link count, le16
            'i_blocks_lo'       : 0,  # Lower 32-bits of block count, le32
            'i_flags'           : EXT4_INODE_FLAGS['FILE_SEC_DEL'],  # Inode flags, le32
            'l_i_version'       : 0,  # Version, le32
            'i_block'           : 0,  # Block map or extent tree, le32[EXT4_N_BLOCKS=15]
            'i_generation'      : 0,  # File version (for NFS), le32
            'i_file_acl_lo'     : 0,  # Lower 32-bits of extended attribute block, le32
            'i_size_high'       : 0,  # Upper 32-bits of file size, le32
            'i_obso_faddr'      : 0,  # (Obsolete) fragment address, le32
            'l_i_blocks_high'   : 0,  # Upper 16-bits of the block count, le16
            'l_i_file_acl_high' : 0,  # Upper 16-bits of the extended attribute block (historically, the file ACL location), le16
            'l_i_uid_high'      : 0,  # Upper 16-bits of the Owner UID, le16
            'l_i_gid_high'      : 0,  # Upper 16-bits of the GID, le16
            'l_i_reserved2'     : 0,  # le32
            'i_extra_isize'     : 0,  # Size of this inode - 128, le16
            'i_pad1'            : 0,  # le16
            'i_ctime_extra'     : 0,  # Extra change time bits. This provides sub-second precision, le32
            'i_mtime_extra'     : 0,  # Extra modification time bits. This provides sub-second precision, le32
            'i_atime_extra'     : 0,  # Extra access time bits. This provides sub-second precision, le32
            'i_crtime'          : 0,  # File creation time, in seconds since the epoch, le32
            'i_crtime_extra'    : 0,  # Extra file creation time bits. This provides sub-second precision, le32
            'i_version_hi'      : 0   # Upper 32-bits for version number, le32
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
    # Check if a is a power of b
    #
    def is_power_of(self, a, b):
        while a > b:
            if a % b:
                return 0
            a /= b

        if a == b:
            return 1
        else:
            return 0

    #
    # Division with round up
    #
    def div_round_up(self, x, y):
        ret = (x + y - 1) / y
        return ret

    #
    # Check if image has Ext4 magic signature
    #
    def is_ext4_has_magic_sig(self):
        return True

    #
    # Check if block group has super block
    #
    def is_ext4_bg_has_sb(self, bg):
        if self.ext4_super_block['s_feature_ro_compat'] & EXT4_FEATURE_RO_COMPAT['EXT4_FEATURE_RO_COMPAT_SPARSE_SUPER'] == 0:
            return True

        if bg == 0 or bg == 1:
            return True

        if self.is_power_of(bg, 3) or self.is_power_of(bg, 5) or self.is_power_of(bg, 7):
            return True

        return False

    #
    # Get block group number
    #
    def get_bg_num(self):
        blocks_count = (self.ext4_super_block['s_blocks_count_hi'] << 32) + self.ext4_super_block['s_blocks_count_lo']
        bg_num = self.div_round_up(blocks_count - self.ext4_super_block['s_first_data_block'], self.ext4_super_block['s_blocks_per_group'])

        return bg_num

    #
    # Get super block's blocks
    #
    def get_sb_blocks(self):
        return 1

    #
    # Get block group descriptor's blocks
    #
    def get_bg_desc_blocks(self):
        if self.ext4_super_block['s_feature_incompat'] & EXT4_FEATURE_INCOMPAT['EXT4_FEATURE_INCOMPAT_64BIT'] != 0 and self.ext4_super_block['s_desc_size'] > 32:
            return self.div_round_up(self.get_bg_num() * 64, EXT4_BLOCK_SZ)
        else:
            #
            # Refer to 's_desc_size'
            # if 'EXT4_FEATURE_COMPAT_HAS_JOURNAL' is set
            #
            return self.div_round_up(self.get_bg_num() * 32, EXT4_BLOCK_SZ)

    #
    # Get reserved GDT's blocks
    #
    def get_bg_desc_reserve_blocks(self):
        return self.div_round_up(self.get_bg_num() * 1024 * self.get_bg_desc_sz(), EXT4_BLOCK_SZ) - self.get_bg_desc_blocks()

    #
    # Get data block bitmap's blocks
    #
    def get_block_bitmap_blocks(self):
        return 1

    #
    # Get inode bitmap's blocks
    #
    def get_inode_bitmap_blocks(self):
        return 1

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

        offset += 68
        self.ext4_super_block['s_blocks_count_hi'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_r_blocks_count_hi'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_free_blocks_count_hi'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_min_extra_isize'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_want_extra_isize'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_flags'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_raid_stride'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_mmp_interval'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_mmp_block'] = self.str2int(self.image[offset:offset+8])

        offset += 8
        self.ext4_super_block['s_raid_stripe_width'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_log_groups_per_flex'] = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_reserved_char_pad2'] = self.str2int(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_reserved_pad'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_kbytes_written'] = self.str2int(self.image[offset:offset+8])

        offset += 8
        self.ext4_super_block['s_reserved'] = self.str2int(self.image[offset:offset+640])

    #
    # Parse Ext4 block group descriptor internally
    #
    def parse_ext4_bg_desc_internal(self, offset):
        self.ext4_block_group_desc['bg_block_bitmap_lo'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_inode_bitmap_lo'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_inode_table_lo'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_free_blocks_count_lo'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_free_inodes_count_lo'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_used_dirs_count_lo'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_flags'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_exclude_bitmap_lo'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_reserved1'] = self.str2int(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_itable_unused_lo'] = self.str2int(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_checksum'] = self.str2int(self.image[offset:offset+2])

        if self.ext4_super_block['s_feature_incompat'] & EXT4_FEATURE_INCOMPAT['EXT4_FEATURE_INCOMPAT_64BIT'] != 0 and self.ext4_super_block['s_desc_size'] > 32:
            offset += 2
            self.ext4_block_group_desc['bg_block_bitmap_hi'] = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_inode_bitmap_hi'] = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_inode_table_hi'] = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_free_blocks_count_hi'] = self.str2int(self.image[offset:offset+2])

            offset += 2
            self.ext4_block_group_desc['bg_free_inodes_count_hi'] = self.str2int(self.image[offset:offset+2])

            offset += 2
            self.ext4_block_group_desc['bg_used_dirs_count_hi'] = self.str2int(self.image[offset:offset+2])

            offset += 2
            self.ext4_block_group_desc['bg_itable_unused_hi'] = self.str2int(self.image[offset:offset+2])

            offset += 2
            self.ext4_block_group_desc['bg_exclude_bitmap_hi'] = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_reserved2'] = self.str2int(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_reserved3'] = self.str2int(self.image[offset:offset+8])

    #
    # Parse Ext4 block group descriptor
    #
    def parse_ext4_bg_desc(self, offset):
        bg_num = self.get_bg_num()

        for i in range(0, bg_num, 1):
            self.parse_ext4_bg_desc_internal(offset + i * self.ext4_super_block['s_desc_size'])

            #
            # Print Ext4 block group descriptor info according to block group #0
            #
            if is_pr_verb is True:
                self.print_ext4_bg_desc_info(i)

    #
    # Parse Ext4 block group
    #
    def parse_ext4_bg(self):
        bg_num = self.get_bg_num()

        blocks_per_group = self.ext4_super_block['s_blocks_per_group']

        for i in range(0, bg_num, 1):
            if self.is_ext4_bg_has_sb(i) is True:
                if i == 0:
                    #
                    # Offset = Super Block Size (Group 0 Padding is included)
                    #
                    offset = self.get_sb_blocks() * EXT4_BLOCK_SZ
                else:
                    #
                    # Offset = Super Block Size
                    #
                    offset = (i * blocks_per_group + self.get_sb_blocks()) * EXT4_BLOCK_SZ
            else:
                offset = i * blocks_per_group * EXT4_BLOCK_SZ

            #
            # Parse Ext4 block group descriptor according to block group #0
            #
            if i == 0:
                self.parse_ext4_bg_desc(offset)

    #
    # Print Ext4 super block info
    #
    def print_ext4_sb_info(self):
        print("\n----------------------------------------")
        print("EXT4 SUPER BLOCK INFO\n")

        print("Total inode count              : " + str(self.ext4_super_block['s_inodes_count']))
        print("Total block count              : " + str((self.ext4_super_block['s_blocks_count_hi'] << 32) + self.ext4_super_block['s_blocks_count_lo']))
        print("Reserved block count           : " + str((self.ext4_super_block['s_r_blocks_count_hi'] << 32) + self.ext4_super_block['s_r_blocks_count_lo']))
        print("Free block count               : " + str((self.ext4_super_block['s_free_blocks_count_hi'] << 32) + self.ext4_super_block['s_free_blocks_count_lo']))
        print("Free inode count               : " + str(self.ext4_super_block['s_free_inodes_count']))
        print("First data block               : " + str(self.ext4_super_block['s_first_data_block']))
        print("Block size                     : " + str(self.ext4_block_sz))
        print("Fragment size (obsolete)       : " + str(int(math.pow(2, (10 + self.ext4_super_block['s_obso_log_frag_size'])))))
        print("Blocks per group               : " + str(self.ext4_super_block['s_blocks_per_group']))
        print("Fragments per group (obsolete) : " + str(self.ext4_super_block['s_obso_frags_per_group']))
        print("Inodes per group               : " + str(self.ext4_super_block['s_inodes_per_group']))
        print("Mount time (seconds)           : " + str(self.ext4_super_block['s_mtime']))
        print("Write time (seconds)           : " + str(self.ext4_super_block['s_wtime']))
        print("Mount count                    : " + str(self.ext4_super_block['s_mnt_count']))
        print("Maximum mount count            : " + str(self.ext4_super_block['s_max_mnt_count']))
        print("Magic signature                : 0x%X" % self.ext4_super_block['s_magic'])

        for k, v in EXT4_STATE.items():
            if v == self.ext4_super_block['s_state']:
                print("File system state              : " + k)

        for k, v in EXT4_ERRORS.items():
            if v == self.ext4_super_block['s_errors']:
                print("Errors behaviour               : " + k)

        print("Minor revision level           : " + str(self.ext4_super_block['s_minor_rev_level']))
        print("Last checked                   : " + str(self.ext4_super_block['s_lastcheck']))
        print("Check interval                 : " + str(self.ext4_super_block['s_checkinterval']))

        for k, v in EXT4_OS.items():
            if v == self.ext4_super_block['s_creator_os']:
                print("OS type                        : " + k)

        for k, v in EXT4_REV_LEVEL.items():
            if v == self.ext4_super_block['s_rev_level']:
                print("Revision level                 : " + k)

        print("Reserved blocks uid            : " + str(self.ext4_super_block['s_def_resuid']))
        print("Reserved blocks gid            : " + str(self.ext4_super_block['s_def_resgid']))

        print("")
        print("")
        print("The Followings For EXT4_DYNAMIC_REV Super Blocks Only")
        print("")

        print("First non-reserved inode    : " + str(self.ext4_super_block['s_first_ino']))
        print("Inode size                  : " + str(self.ext4_super_block['s_inode_size']))
        print("Block group number          : " + str(self.ext4_super_block['s_block_group_nr']))

        feature_compat = ""
        for k, v in EXT4_FEATURE_COMPAT.items():
            if (v & self.ext4_super_block['s_feature_compat']) != 0:
                feature_compat += k + " "
        print("Compatible feature          : " + feature_compat)

        feature_incompat = ""
        for k, v in EXT4_FEATURE_INCOMPAT.items():
            if (v & self.ext4_super_block['s_feature_incompat']) != 0:
                feature_incompat += k + " "
        print("Incompatible feature        : " + feature_incompat)

        feature_ro_compat = ""
        for k, v in EXT4_FEATURE_RO_COMPAT.items():
            if (v & self.ext4_super_block['s_feature_ro_compat']) != 0:
                feature_ro_compat += k + " "
        print("Readonly-compatible feature : " + feature_ro_compat)

        print("UUID                        : %x" % self.ext4_super_block['s_uuid'])
        print("Volume name                 : " + self.ext4_super_block['s_volume_name'])
        print("Last mounted on             : " + self.ext4_super_block['s_last_mounted'])
        print("Bitmap algorithm usage      : " + str(self.ext4_super_block['s_algorithm_usage_bitmap']))

        print("")
        print("")
        print("Performance hints Directory preallocation should only happen")
        print("if the EXT4_FEATURE_COMPAT_DIR_PREALLOC flag is on")
        print("")

        print("Blocks preallocated for files : " + str(self.ext4_super_block['s_prealloc_blocks']))
        print("Blocks preallocated for dirs  : " + str(self.ext4_super_block['s_prealloc_dir_blocks']))
        print("Reserved GDT blocks           : " + str(self.ext4_super_block['s_reserved_gdt_blocks']))

        print("")
        print("")
        print("Journaling support valid if EXT4_FEATURE_COMPAT_HAS_JOURNAL set")
        print("")

        print("Journal UUID                         : %x" % self.ext4_super_block['s_journal_uuid'])
        print("Journal inode                        : " + str(self.ext4_super_block['s_journal_inum']))
        print("Journal device                       : " + str(self.ext4_super_block['s_journal_dev']))
        print("Orphaned inodes to delete            : " + str(self.ext4_super_block['s_last_orphan']))
        print("HTREE hash seed                      : %x" % self.ext4_super_block['s_hash_seed'])

        for k, v in EXT4_DEFAULT_HASH_VER.items():
            if v == self.ext4_super_block['s_def_hash_version']:
                print("Default hash version for dirs hashes : " + k)

        print("Reserved char padding                : " + str(self.ext4_super_block['s_reserved_char_pad']))
        print("Group descriptors size               : " + str(self.ext4_super_block['s_desc_size']))

        default_mount_opts = ""
        for k, v in EXT4_DEFAULT_MOUNT_OPTS.items():
            if (v & self.ext4_super_block['s_default_mount_opts']) != 0:
                default_mount_opts += k + " "
        print("Default mount options                : " + default_mount_opts)

        print("First metablock block group          : " + str(self.ext4_super_block['s_first_meta_bg']))
        print("Filesystem-created time (seconds)    : " + str(self.ext4_super_block['s_mkfs_time']))
        print("Journal backup                       : %x" % self.ext4_super_block['s_jnl_blocks'])

        print("")
        print("")
        print("64bit support valid if EXT4_FEATURE_INCOMPAT_64BIT")
        print("")

        print("Required extra isize             : " + str(self.ext4_super_block['s_min_extra_isize']))
        print("Desired extra isize              : " + str(self.ext4_super_block['s_want_extra_isize']))

        misc_flags = ""
        for k, v in EXT4_MISC_FLAGS.items():
            if (v & self.ext4_super_block['s_flags']) != 0:
                misc_flags += k + " "
        print("Misc flags                       : " + misc_flags)

        print("RAID stride                      : " + str(self.ext4_super_block['s_raid_stride']))
        print("MMP checking wait time (seconds) : " + str(self.ext4_super_block['s_mmp_interval']))
        print("MMP blocks                       : " + str(self.ext4_super_block['s_mmp_block']))
        print("RAID stripe width                : " + str(self.ext4_super_block['s_raid_stripe_width']))
        print("Flexible block size              : " + str(int(math.pow(2, self.ext4_super_block['s_log_groups_per_flex']))))
        print("Reserved char padding 2          : " + str(self.ext4_super_block['s_reserved_char_pad2']))
        print("Reserved padding                 : " + str(self.ext4_super_block['s_reserved_pad']))
        print("KiB writtten                     : " + str(self.ext4_super_block['s_kbytes_written']))

    #
    # Print Ext4 block group descriptors info
    #
    def print_ext4_bg_desc_info(self, bg_index):
        print("\n----------------------------------------")
        print("EXT4 BLOCK GROUP DESCRIPTOR #%d INFO\n" % bg_index)

        print("Block bitmap at           : " + str((self.ext4_block_group_desc['bg_block_bitmap_hi'] << 32) + self.ext4_block_group_desc['bg_block_bitmap_lo']))
        print("Inode bitmap at           : " + str((self.ext4_block_group_desc['bg_inode_bitmap_hi'] << 32) + self.ext4_block_group_desc['bg_inode_bitmap_lo']))
        print("Inode table at            : " + str((self.ext4_block_group_desc['bg_inode_table_hi'] << 32) + self.ext4_block_group_desc['bg_inode_table_lo']))
        print("Free blocks count         : " + str((self.ext4_block_group_desc['bg_free_blocks_count_hi'] << 32) + self.ext4_block_group_desc['bg_free_blocks_count_lo']))
        print("Free inodes count         : " + str((self.ext4_block_group_desc['bg_free_inodes_count_hi'] << 32) + self.ext4_block_group_desc['bg_free_inodes_count_lo']))
        print("Used directories count    : " + str((self.ext4_block_group_desc['bg_used_dirs_count_hi'] << 32) + self.ext4_block_group_desc['bg_used_dirs_count_lo']))

        bg_flags = ""
        for k, v in EXT4_BG_FLAGS.items():
            if (v & self.ext4_block_group_desc['bg_flags']) != 0:
                bg_flags += k + " "
        print("Block group flags         : " + bg_flags)

        print("Exclusion bitmap at       : " + str((self.ext4_block_group_desc['bg_exclude_bitmap_hi'] << 32) + self.ext4_block_group_desc['bg_exclude_bitmap_lo']))
        print("Unused inode count        : " + str((self.ext4_block_group_desc['bg_itable_unused_hi'] << 32) + self.ext4_block_group_desc['bg_itable_unused_lo']))
        print("Group descriptor checksum : " + str(self.ext4_block_group_desc['bg_checksum']))

    #
    # Run routine
    #
    def run(self):
        global is_pr_verb

        #
        # Check image type magic signature
        #
        if self.is_ext4_has_magic_sig() is False:
            print("\nERROR: invalid image type!\n")
            return

        #
        # Parse Ext4 super block
        #
        offset = EXT4_GROUP_0_PAD_SZ
        self.parse_ext4_sb(offset)

        #
        # Print Ext4 super block info
        #
        if is_pr_verb is True:
            self.print_ext4_sb_info()

        #
        # Parse Ext4 block group
        #
        # Attention: 's_first_meta_b' is 0
        #
        self.parse_ext4_bg()

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
