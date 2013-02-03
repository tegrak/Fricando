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
# python ext4img-parser.py -v -f ext4.img -d ext4-dump
#

import os, sys
import getopt
import math
import time

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
# Ext4 Block Size
#
EXT4_BLOCK_SZ       = 4096
EXT4_MIN_BLOCK_SIZE = 1024
EXT4_MAX_BLOCK_SIZE = 65536

#
# Ext4 Inode
#
EXT4_BAD_INO            = 1
EXT4_ROOT_INO           = 2
EXT4_BOOT_LOADER_INO    = 5
EXT4_UNDEL_DIR_INO      = 6
EXT4_RESIZE_INO         = 7
EXT4_JOURNAL_INO        = 8
EXT4_GOOD_OLD_FIRST_INO = 11

#
# Ext4 Block Group
#
EXT4_GROUP_0_PAD_SZ = 1024

#
# Ext4 Super Block
#
EXT4_SUPER_MAGIC = 0xEF53

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

EXT4_DEFAULT_MOUNT_OPTS = {
    'EXT2_DEFM_DEBUG'          : 0x0001,
    'EXT2_DEFM_BSDGROUPS'      : 0x0002,
    'EXT2_DEFM_XATTR_USER'     : 0x0004,
    'EXT2_DEFM_ACL'            : 0x0008,
    'EXT2_DEFM_UID16'          : 0x0010,
    'EXT3_DEFM_JMODE_DATA'     : 0x0020,
    'EXT3_DEFM_JMODE_ORDERED'  : 0x0040,
    'EXT3_DEFM_JMODE'          : 0x0060,
    'EXT3_DEFM_JMODE_WBACK'    : 0x0080,
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

#
# Ext4 Block Group Descriptors
#
EXT4_BG_FLAGS = {
    'EXT2_BG_INODE_UNINIT' : 0x0001,
    'EXT2_BG_BLOCK_UNINIT' : 0x0002,
    'EXT2_BG_INODE_ZEROED' : 0x0004
    }

#
# Ext4 Inode Table
#
EXT4_INODE_ENTRY_SZ = 128

EXT4_NDIR_BLOCKS = 12
EXT4_IND_BLOCK   = EXT4_NDIR_BLOCKS
EXT4_DIND_BLOCK  = EXT4_IND_BLOCK + 1
EXT4_TIND_BLOCK  = EXT4_DIND_BLOCK + 1
EXT4_N_BLOCKS    = EXT4_TIND_BLOCK + 1

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
    'EXT4_SECRM_FL'        : 0x1,  # This file requires secure deletion. (not implemented)
    'EXT4_UNRM_FL'         : 0x2,  # This file should be preserved should undeletion be desired. (not implemented)
    'EXT4_COMPR_FL'        : 0x4,  # File is compressed. (not really implemented)
    'EXT4_SYNC_FL'         : 0x8,  # All writes to the file must be synchronous.
    'EXT4_IMMUTABLE_FL'    : 0x10,  # File is immutable.
    'EXT4_APPEND_FL'       : 0x20,  # File can only be appended.
    'EXT4_NODUMP_FL'       : 0x40,  # The dump utility should not dump this file.
    'EXT4_NOATIME_FL'      : 0x80,  # Do not update access time.
    'EXT4_DIRTY_FL'        : 0x100,  # Dirty compressed file. (not used)
    'EXT4_COMPRBLK_FL'     : 0x200,  # File has one or more compressed clusters. (not used)
    'EXT4_NOCOMPR_FL'      : 0x400,  # Do not compress file. (not used)
    'EXT4_ECOMPR_FL'       : 0x800,  # Compression error. (not used)
    'EXT4_INDEX_FL'        : 0x1000,  # Directory has hashed indexes.
    'EXT4_IMAGIC_FL'       : 0x2000,  # AFS magic directory.
    'EXT4_JOURNAL_DATA_FL' : 0x4000,  # File data must always be written through the journal.
    'EXT4_NOTAIL_FL'       : 0x8000,  # File tail should not be merged.
    'EXT4_DIRSYNC_FL'      : 0x10000,  # All directory entry data should be written synchronously (see dirsync).
    'EXT4_TOPDIR_FL'       : 0x20000,  # Top of directory hierarchy.
    'EXT4_HUGE_FILE_FL'    : 0x40000,  # This is a huge file.
    'EXT4_EXTENTS_FL'      : 0x80000,  # Inode uses extents.
    'EXT4_EA_INODE_FL'     : 0x200000,  # Inode used for a large extended attribute.
    'EXT4_EOFBLOCKS_FL'    : 0x400000,  # This file has blocks allocated past EOF.
    'EXT4_RESERVED_FL'     : 0x80000000,  # Reserved for ext4 library.

    #
    # Aggregate flags
    #
    'EXT4_FL_USER_VISIBLE'    : 0x4BDFFF,  # User-visible flags.
    'EXT4_FL_USER_MODIFIABLE' : 0x4B80FF,  # User-modifiable flags. 
    }

#
# Ext4 Extent Tree
#
EXT4_EXTENT_TREE_MAGIC = 0xF30A

#
# Ext4 Directory Entries
#
EXT4_NAME_LEN = 255

EXT4_HTREE_NAME_LEN = 4

EXT4_FILE_TYPE = {
    'EXT4_FT_UNKNOWN'  : 0x0,
    'EXT4_FT_REG_FILE' : 0x1,
    'EXT4_FT_DIR'      : 0x2,
    'EXT4_FT_CHRDEV'   : 0x3,
    'EXT4_FT_BLKDEV'   : 0x4,
    'EXT4_FT_FIFO'     : 0x5,
    'EXT4_FT_SOCK'     : 0x6,
    'EXT4_FT_SYMLINK'  : 0x7
    }

#
# Ext4 Extended Attributes
#
EXT4_XATTR_MAGIC = 0xEA020000

#
# Ext4 Journal, jbd2
#
EXT4_JNL_BACKUP_BLOCKS = 1

JBD2_MAGIC_NUMBER = 0xC03B3998

#
# i.e., 'JBD2_CHECKSUM_BYTES = (32 / sizeof(u32))'
#
JBD2_CHECKSUM_BYTES = (32 / 4)

EXT4_JNL_BLOCK_TYPE = {
    'JBD2_DESCRIPTOR_BLOCK'    : 1,
    'JBD2_COMMIT_BLOCK'        : 2,
    'JBD2_SUPERBLOCK_V1'       : 3,
    'JBD2_SUPERBLOCK_V2'       : 4,
    'JBD2_REVOKE_BLOCK'        : 5
    }

EXT4_JNL_FEATURE_COMPAT = {
    'JBD2_FEATURE_COMPAT_CHECKSUM' : 0x00000001
    }

EXT4_JNL_FEATURE_INCOMPAT = {
    'JBD2_FEATURE_INCOMPAT_REVOKE'       : 0x00000001,
    'JBD2_FEATURE_INCOMPAT_64BIT'        : 0x00000002,
    'JBD2_FEATURE_INCOMPAT_ASYNC_COMMIT' : 0x00000004
    }

EXT4_JNL_FLAGS = {
    'JBD2_FLAG_ESCAPE'    : 1,
    'JBD2_FLAG_SAME_UUID' : 2,
    'JBD2_FLAG_DELETED'   : 4,
    'JBD2_FLAG_LAST_TAG'  : 8
    }

EXT4_JNL_CHKSUM_TYPE = {
    'JBD2_CRC32_CHKSUM' : 1,
    'JBD2_MD5_CHKSUM'   : 2,
    'JBD2_SHA1_CHKSUM'  : 3
    }

#
# Ext4 Hash
#
EXT4_HASH_VERSION = {
    'DX_HASH_LEGACY'            : 0x0,
    'DX_HASH_HALF_MD4'          : 0x1,
    'DX_HASH_TEA'               : 0x2,
    'DX_HASH_LEGACY_UNSIGNED'   : 0x3,
    'DX_HASH_HALF_MD4_UNSIGNED' : 0x4,
    'DX_HASH_TEA_UNSIGNED'      : 0x5
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
            's_def_hash_version'   : EXT4_HASH_VERSION['DX_HASH_TEA'],  # Default hash algorithm to use for directory hashes, u8
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
            'i_flags'           : EXT4_INODE_FLAGS['EXT4_SECRM_FL'],  # Inode flags, le32
            'l_i_version'       : 0,  # Version, le32
            'i_block'           : 0,  # Block map for ext2/3 or extent tree for ext4 (the extents flag must be set), le32[EXT4_N_BLOCKS=15]
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
        # Ext4 extent tree
        #

        #
        # Ext4 extent header
        #
        self.ext4_extent_header = {
            'eh_magic'      : EXT4_EXTENT_TREE_MAGIC,  # Magic number, le16
            'eh_entries'    : 0,  # Number of valid entries following the header, le16
            'eh_max'        : 0,  # Maximum number of entries that could follow the header, le16
            'eh_depth'      : 0,  # Depth of this extent node in the extent tree;
                                  # 0 = this extent node points to data blocks;
                                  # otherwise, this extent node points to other extent nodes, le16
            'eh_generation' : 0,  # Generation of the tree (Used by Lustre, but not standard ext4), le32
            }

        #
        # Ext4 extent index node
        #
        self.ext4_extent_idx = {
            'ei_block'   : 0,  # This index node covers file blocks from 'block' onward, le32
            'ei_leaf_lo' : 0,  # Lower 32-bits of the block number of the extent node that is the next level lower in the tree;
                               # The tree node pointed to can be either another internal node or a leaf node, described below, le32
            'ei_leaf_hi' : 0,  # Upper 16-bits of the previous field, le16
            'ei_unused'  : 0,  # u16
            }

        #
        # Ext4 extent leaf node
        #
        self.ext4_extent = {
            'ee_block'    : 0,  # First file logical block number that this extent covers, le32
            'ee_len'      : 0,  # Number of blocks covered by extent, le16
            'ee_start_hi' : 0,  # Upper 16-bits of physical block number to which this extent points, le16
            'ee_start_lo' : 0,  # Lower 32-bits of physical block number to which this extent points, le32
            }

        #
        # Ext4 linear directory entries
        #

        #
        # Ext4 linear directory entry, used if 'file_type' not set
        #
        self.ext4_dir_entry = {
            'inode'    : 0,  # Number of the inode that this directory entry points to, le32
            'rec_len'  : 0,  # Length of this directory entry, le16
            'name_len' : 0,  # Length of the file name, le16
            'name'     : "",  # File name, char[EXT4_NAME_LEN]
        }

        #
        # Ext4 linear directory entry 2, used as default
        #
        self.ext4_dir_entry_2 = {
            'inode'     : 0,  # Number of the inode that this directory entry points to, le32
            'rec_len'   : 0,  # Length of this directory entry, le16
            'name_len'  : 0,  # Length of the file name, u8
            'file_type' : EXT4_FILE_TYPE['EXT4_FT_UNKNOWN'],  # File type code, u8
            'name'      : "",  # File name, char[EXT4_NAME_LEN]
            }

        #
        # Ext4 hash tree directory entries, used if 'EXT4_INODE_FLAGS['EXT4_INDEX_FL']' set
        #

        #
        # Ext4 htree directory root
        #
        self.dx_root = {
            'dot_inode'         : 0,  # Inode number of this directory, le32
            'dot_rec_len'       : 0,  # Length of this record, 12, le16
            'dot_name_len'      : 0,  # Length of the name, 1, u8
            'dot_file_type'     : 0,  # File type of this entry, 0x2 (directory) (if the feature flag is set), u8
            'dot_name'          : "",  # ".\0\0\0", char[EXT4_HTREE_NAME_LEN]
            'dot_dot_inode'     : 0,  # Inode number of parent directory, le32
            'dot_dot_rec_len'   : 0,  # Record length, block_size - 12, le16
            'dot_dot_name_len'  : 0,  # Length of the name, u8
            'dot_dot_file_type' : 0,  # File type of this entry, 0x2 (directory) (if the feature flag is set), u8
            'dot_dot_name'      : "",   # "..\0\0", char[EXT4_HTREE_NAME_LEN]
            'reserved_zero'     : 0,  # Zero, le32
            'hash_version'      : EXT4_HASH_VERSION['DX_HASH_LEGACY'],  # Hash version, u8
            'info_length'       : 0,  # Length of the tree information, u8
            'indirect_levels'   : 0,  # Depth of the htree, u8
            'unused_flags'      : 0,  # u8
            'limit'             : 0,  # Maximum number of dx_entries that can follow this header, le16
            'count'             : 0,  # Actual number of dx_entries that follow this header, le16
            'block'             : 0,  # The block number (within the directory file) that goes with hash=0, le32
            
            #
            # Type of 'dx_entry'
            #
            'entries'           : 0,  # As many 8-byte 'dx_entry' as fits in the rest of the data block, le32[2]
            }

        #
        # Ext4 htree directory interior node
        #
        self.dx_node = {
            'fake_inode'     : 0,  # Zero, to make it look like this entry is not in use, le32
            'fake_rec_len'   : 0,  # The size of the block, in order to hide all of the dx_node data, le16
            'fake_name_len'  : 0,  # Zero. There is no name for this "unused" directory entry, u8
            'fake_file_type' : 0,  # Zero. There is no file type for this "unused" directory entry, u8
            'limit'          : 0,  # Maximum number of dx_entries that can follow this header, le16
            'count'          : 0,  # Actual number of dx_entries that follow this header, le16
            'block'          : 0,  # The block number (within the directory file) that goes with the lowest hash value of this block. This value is stored in the parent block, le32

            #
            # Type of 'dx_entry'
            #
            'entries'        : 0,  # As many 8-byte 'dx_entry' as fits in the rest of the data block, le32[2]
            }

        #
        # Ext4 htree directory entry
        #
        self.dx_entry = {
            'hash'  : 0,  # Hash code, le32
            'block' : 0,  # Block number (within the directory file, not filesystem blocks) of the next node in the htree, le32
            }

        #
        # Ext4 extended attributes
        #

        #
        # Ext4 extended attributes header
        #
        self.ext4_xattr_header = {
            'h_magic'    : EXT4_XATTR_MAGIC,  # Magic number for identification, le32
            'h_refcount' : 0,  # Reference count, le32
            'h_blocks'   : 0,  # Number of disk blocks used, le32
            'h_hash'     : 0,  # Hash value of all attributes, le32
            'h_reserved' : 0,  # le32[4]
            }

        #
        # Ext4 extended attributes entry
        #
        self.ext4_xattr_entry = {
            'e_name_len'    : 0,  # Length of name, u8
            'e_name_index'  : 0,  # Attribute name index, u8
            'e_value_offs'  : 0,  # Location of this attribute's value on the disk block where it is stored,
                                  # Multiple attributes can share the same value, le16
            'e_value_block' : 0,  # The disk block where the value is stored,
                                  # Zero indicates the value is in the same block as this entry, le32
            'e_value_size'  : 0,  # Length of attribute value, le32
            'e_hash'        : 0,  # Hash value of name and value, le32
            'e_name'        : "",  # Attribute name. Does not include trailing NULL, char['e_name_len']
            }

        #
        # Ext4 journal, jbd2
        #

        #
        # Ext4 journal block header
        #
        self.journal_header_s = {
            'h_magic'     : JBD2_MAGIC_NUMBER,  # jbd2 magic number, be32
            'h_blocktype' : EXT4_JNL_BLOCK_TYPE['JBD2_DESCRIPTOR_BLOCK'],  # Description of what this block contains, be32
            'h_sequence'  : 0,  # The transaction ID that goes with this block, be32
            }

        #
        # Ext4 journal super block
        #
        self.journal_superblock_s = {
            's_header'            : 0,  # Common header identifying this as a superblock, be32[3]

            #
            # Static information describing the journal.
            #
            's_blocksize'         : 0,  # Journal device block size, be32
            's_maxlen'            : 0,  # Total number of blocks in this journal, be32
            's_first'             : 0,  # First block of log information, be32

            #
            # Dynamic information describing the current state of the log.
            #
            's_sequence'          : 0,  # First commit ID expected in log, be32
            's_start'             : 0,  # Block number of the start of log. If zero, the journal is clean, be32
            's_errno'             : 0,  # Error value, as set by jbd2_journal_abort(), be32

            #
            # The remaining fields are only valid in a version 2 superblock.
            #
            's_feature_compat'    : EXT4_JNL_FEATURE_COMPAT['JBD2_FEATURE_COMPAT_CHECKSUM'],  # Compatible feature set, be32
            's_feature_incompat'  : EXT4_JNL_FEATURE_INCOMPAT['JBD2_FEATURE_INCOMPAT_REVOKE'],  # Incompatible feature set, be32
            's_feature_ro_compat' : 0,  # Read-only compatible feature set. There aren't any of these currently, be32
            's_uuid'              : 0,  # 128-bit uuid for journal.
                                        # This is compared against the copy in the ext4 super block at mount time, u8[16]
            's_nr_users'          : 0,  # Number of file systems sharing this journal, be32
            's_dynsuper'          : 0,  # Location of dynamic super block copy, be32
            's_max_transaction'   : 0,  # Limit of journal blocks per transaction, be32
            's_max_trans_data'    : 0,  # Limit of data blocks per transaction, be32
            's_padding'           : 0,  # u32[44]
            's_users'             : 0,  # ids of all file systems sharing the log, u8[16*48]
            }

        #
        # Ext4 journal descriptor block
        #
        self.journal_block_tag_s = {
            't_blocknr'      : 0,  # Lower 32-bits of the location of where the corresponding data block should end up on disk, be32
            't_flags'        : EXT4_JNL_FLAGS['JBD2_FLAG_ESCAPE'],  # Flags that go with the descriptor, be32

            #
            # This next field is only present
            # if the super block indicates support for 64-bit block numbers.
            # i.e., EXT4_JNL_FEATURE_INCOMPAT['JBD2_FEATURE_INCOMPAT_64BIT'] set
            #
            't_blocknr_high' : 0,  # Upper 32-bits of the location of where the corresponding data block should end up on disk, be32

            #
            # This field appears to be open coded.
            # It always comes at the end of the tag, after t_flags or t_blocknr_high.
            # This field is not present if the "same UUID" flag is set,
            # i.e., EXT4_JNL_FLAGS['JBD2_FLAG_SAME_UUID'] set
            #
            'uuid'           : 0,  # A UUID to go with this tag.
                                   # This field appears to be copied from a field in struct journal_s that is never set,
                                   # which means that the UUID is probably all zeroes. Or perhaps it will contain garbage, char[16]
            }

        self.journal_desc_block_s = {
            'db_header'    : 0,  # Common header, be32[3]
            'db_block_tag' : 0,  # Enough tags either to fill up the block
                                 # or to describe all the data blocks that follow this descriptor block, sizeof('journal_block_tag_s')
            }

        #
        # Ext4 journal revocation block
        #
        self.jbd2_journal_revoke_header_s = {
            'r_header' : 0,  # Common block header, be32[3]
            'r_count'  : 0,  # Number of bytes used in this block, be32
            'blocks'   : 0,  # Blocks to revoke, be32/be64
            }

        #
        # Ext4 journal commit block
        #
        self.commit_header = {
            'c_header'      : 0,  # Common block header, be32[3]
            'h_chksum_type' : EXT4_JNL_CHKSUM_TYPE['JBD2_CRC32_CHKSUM'],
                                  # The type of checksum to use to verify the integrity of the data blocks in the transaction, unsigned char
            'h_chksum_size' : 0,  # The number of bytes used by the checksum, unsigned char
            'h_padding'     : 0,  # unsigned char[2]
            'h_chksum'      : 0,  # 32 bytes of space to store checksums, be32[JBD2_CHECKSUM_BYTES]
            'h_commit_sec'  : 0,  # The time that the transaction was committed, in seconds since the epoch, be64
            'h_commit_nsec' : 0,  # Nanoseconds component of the above timestamp, be32
            }

    #
    # Convert string to integer with little-endian order
    #
    def str2int_le(self, str_list):
        i = 0
        data = 0
        str_len = len(str_list)

        while (i < str_len):
            data += ord(str_list[i]) << (i * 8)
            i += 1

        return data

    #
    # Convert string to integer with big-endian order
    #
    def str2int_be(self, str_list):
        i = 0
        data = 0
        str_len = len(str_list)
        j = str_len - 1

        while (i < str_len):
            data += ord(str_list[j]) << (i * 8)
            i += 1
            j -= 1

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
    # Get block group count
    #
    def get_bg_count(self):
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
            return self.div_round_up(self.get_bg_count() * 64, EXT4_BLOCK_SZ)
        else:
            #
            # Refer to 's_desc_size'
            # if 'EXT4_FEATURE_COMPAT_HAS_JOURNAL' is set
            #
            return self.div_round_up(self.get_bg_count() * 32, EXT4_BLOCK_SZ)

    #
    # Get reserved GDT's blocks
    #
    def get_bg_desc_reserve_blocks(self):
        return self.div_round_up(self.get_bg_count() * 1024 * self.get_bg_desc_sz(), EXT4_BLOCK_SZ) - self.get_bg_desc_blocks()

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
    # Get inode count used
    #
    def get_inode_count_used(self):
        return self.ext4_super_block['s_inodes_count'] - self.ext4_super_block['s_free_inodes_count']

    #
    # Parse Ext4 super block
    #
    def parse_ext4_sb(self, offset):
        self.ext4_super_block['s_inodes_count'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_blocks_count_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_r_blocks_count_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_free_blocks_count_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_free_inodes_count'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_first_data_block'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_log_block_size'] = self.str2int_le(self.image[offset:offset+4])
        self.ext4_block_sz = int(math.pow(2, (10 + self.ext4_super_block['s_log_block_size'])))

        offset += 4
        self.ext4_super_block['s_obso_log_frag_size'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_blocks_per_group'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_obso_frags_per_group'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_inodes_per_group'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_mtime'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_wtime'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_mnt_count'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_max_mnt_count'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_magic'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_state'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_errors'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_minor_rev_level'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_lastcheck'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_checkinterval'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_creator_os'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_rev_level'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_def_resuid'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_def_resgid'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_first_ino'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_inode_size'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_block_group_nr'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_feature_compat'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_feature_incompat'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_feature_ro_compat'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_uuid'] = self.str2int_le(self.image[offset:offset+16])

        offset += 16
        self.ext4_super_block['s_volume_name'] = self.image[offset:offset+16].split("\x00")[0]

        offset += 16
        self.ext4_super_block['s_last_mounted'] = self.image[offset:offset+64].split("\x00")[0]

        offset += 64
        self.ext4_super_block['s_algorithm_usage_bitmap'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_prealloc_blocks'] = self.str2int_le(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_prealloc_dir_blocks'] = self.str2int_le(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_reserved_gdt_blocks'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_journal_uuid'] = self.str2int_le(self.image[offset:offset+16])

        offset += 16
        self.ext4_super_block['s_journal_inum'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_journal_dev'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_last_orphan'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_hash_seed'] = self.str2int_le(self.image[offset:offset+16])

        offset += 16
        self.ext4_super_block['s_def_hash_version'] = self.str2int_le(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_reserved_char_pad'] = self.str2int_le(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_desc_size'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_default_mount_opts'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_first_meta_bg'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_mkfs_time'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_jnl_blocks'] = self.str2int_le(self.image[offset:offset+68])

        offset += 68
        self.ext4_super_block['s_blocks_count_hi'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_r_blocks_count_hi'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_free_blocks_count_hi'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_min_extra_isize'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_want_extra_isize'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_flags'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_raid_stride'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_mmp_interval'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_mmp_block'] = self.str2int_le(self.image[offset:offset+8])

        offset += 8
        self.ext4_super_block['s_raid_stripe_width'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_super_block['s_log_groups_per_flex'] = self.str2int_le(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_reserved_char_pad2'] = self.str2int_le(self.image[offset:offset+1])

        offset += 1
        self.ext4_super_block['s_reserved_pad'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_super_block['s_kbytes_written'] = self.str2int_le(self.image[offset:offset+8])

        offset += 8
        self.ext4_super_block['s_reserved'] = self.str2int_le(self.image[offset:offset+640])

        #
        # Print Ext4 super block info
        #
        self.print_ext4_sb_info()

    #
    # Parse Ext4 block group descriptor internally
    #
    def parse_ext4_bg_desc_internal(self, offset):
        self.ext4_block_group_desc['bg_block_bitmap_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_inode_bitmap_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_inode_table_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_free_blocks_count_lo'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_free_inodes_count_lo'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_used_dirs_count_lo'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_flags'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_exclude_bitmap_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_reserved1'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_block_group_desc['bg_itable_unused_lo'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_block_group_desc['bg_checksum'] = self.str2int_le(self.image[offset:offset+2])

        if self.ext4_super_block['s_feature_incompat'] & EXT4_FEATURE_INCOMPAT['EXT4_FEATURE_INCOMPAT_64BIT'] != 0 and self.ext4_super_block['s_desc_size'] > 32:
            offset += 2
            self.ext4_block_group_desc['bg_block_bitmap_hi'] = self.str2int_le(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_inode_bitmap_hi'] = self.str2int_le(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_inode_table_hi'] = self.str2int_le(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_free_blocks_count_hi'] = self.str2int_le(self.image[offset:offset+2])

            offset += 2
            self.ext4_block_group_desc['bg_free_inodes_count_hi'] = self.str2int_le(self.image[offset:offset+2])

            offset += 2
            self.ext4_block_group_desc['bg_used_dirs_count_hi'] = self.str2int_le(self.image[offset:offset+2])

            offset += 2
            self.ext4_block_group_desc['bg_itable_unused_hi'] = self.str2int_le(self.image[offset:offset+2])

            offset += 2
            self.ext4_block_group_desc['bg_exclude_bitmap_hi'] = self.str2int_le(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_reserved2'] = self.str2int_le(self.image[offset:offset+4])

            offset += 4
            self.ext4_block_group_desc['bg_reserved3'] = self.str2int_le(self.image[offset:offset+8])

    #
    # Parse Ext4 extent tree
    #
    def parse_ext4_extent_tree(self, offset):
        self.ext4_inode_table['i_block'] = self.str2int_le(self.image[offset:offset+60])

        self.ext4_extent_header['eh_magic'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_extent_header['eh_entries'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_extent_header['eh_max'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_extent_header['eh_depth'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_extent_header['eh_generation'] = self.str2int_le(self.image[offset:offset+4])

        for i in range(0, self.ext4_extent_header['eh_entries'], 1):
            if self.ext4_extent_header['eh_depth'] > 0:
                offset += 4
                self.ext4_extent_idx['ei_block'] = self.str2int_le(self.image[offset:offset+4])

                offset += 4
                self.ext4_extent_idx['ei_leaf_lo'] = self.str2int_le(self.image[offset:offset+4])

                offset += 4
                self.ext4_extent_idx['ei_leaf_hi'] = self.str2int_le(self.image[offset:offset+2])

                offset += 2
                self.ext4_extent_idx['ei_unused'] = self.str2int_le(self.image[offset:offset+2])

                #
                # Parse Ext4 extent tree's leaf nodes
                #
                '''
                Add code here
                '''
            elif self.ext4_extent_header['eh_depth'] == 0:
                offset += 4
                self.ext4_extent['ee_block'] = self.str2int_le(self.image[offset:offset+4])

                offset += 4
                self.ext4_extent['ee_len'] = self.str2int_le(self.image[offset:offset+2])

                offset += 2
                self.ext4_extent['ee_start_hi'] = self.str2int_le(self.image[offset:offset+2])

                offset += 2
                self.ext4_extent['ee_start_lo'] = self.str2int_le(self.image[offset:offset+4])
            else:
                pass

    #
    # Parse Ext4 inode in inode table internally
    #
    def parse_ext4_bg_inode_internal(self, offset):
        self.ext4_inode_table['i_mode'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['i_uid'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['i_size_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_atime'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_ctime'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_mtime'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_dtime'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_gid'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['i_links_count'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['i_blocks_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_flags'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['l_i_version'] = self.str2int_le(self.image[offset:offset+4])

        #
        # Parse Ext4 extent tree
        #
        # 'EXT4_FEATURE_INCOMPAT['EXT4_FEATURE_INCOMPAT_EXTENTS']' MUST set for Ext4
        #
        offset += 4
        self.parse_ext4_extent_tree(offset)

        offset += 60
        self.ext4_inode_table['i_generation'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_file_acl_lo'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_size_high'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_obso_faddr'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['l_i_blocks_high'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['l_i_file_acl_high'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['l_i_uid_high'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['l_i_gid_high'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['l_i_reserved2'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_extra_isize'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['i_pad1'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_inode_table['i_ctime_extra'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_mtime_extra'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_atime_extra'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_crtime'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_crtime_extra'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_inode_table['i_version_hi'] = self.str2int_le(self.image[offset:offset+4])

    #
    # Parse Ext4 extended attributes, especially for ACLs
    #
    def parse_ext4_xattr(self, offset):
        self.ext4_xattr_header['h_magic'] = self.str2int_le(self.image[offset:offset+4])

        if self.ext4_xattr_header['h_magic'] != EXT4_XATTR_MAGIC:
            return

        offset += 4
        self.ext4_xattr_header['h_refcount'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_xattr_header['h_blocks'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_xattr_header['h_hash'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_xattr_header['h_reserved'] = self.str2int_le(self.image[offset:offset+16])

        offset += 16
        self.ext4_xattr_entry['e_name_len'] = self.str2int_le(self.image[offset:offset+1])

        offset += 1
        self.ext4_xattr_entry['e_name_index'] = self.str2int_le(self.image[offset:offset+1])

        offset += 1
        self.ext4_xattr_entry['e_value_offs'] = self.str2int_le(self.image[offset:offset+2])

        offset += 2
        self.ext4_xattr_entry['e_value_block'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_xattr_entry['e_value_size'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_xattr_entry['e_hash'] = self.str2int_le(self.image[offset:offset+4])

        offset += 4
        self.ext4_xattr_entry['e_name'] = self.image[offset:offset+self.ext4_xattr_entry['e_name_len']] + '\x00'

        #
        # Print Ext4 extended attributes info
        #
        if is_pr_verb is True:
            self.print_ext4_xattr_info()

    #
    # Parse Ext4 directory entries internally
    #
    def parse_ext4_dir_entry_internal(self, offset):
        rec_len = 0

        if self.ext4_inode_table['i_flags'] & EXT4_INODE_FLAGS['EXT4_INDEX_FL'] != 0:
            #
            # Parse Ext4 htree directory entries
            #
            '''
            Add code here
            '''
        else:
            #
            # Parse Ext4 linear directory entries
            #
            self.ext4_dir_entry_2['inode'] = self.str2int_le(self.image[offset:offset+4])

            offset += 4
            self.ext4_dir_entry_2['rec_len'] = self.str2int_le(self.image[offset:offset+2])
            rec_len = self.ext4_dir_entry_2['rec_len']

            offset += 2
            self.ext4_dir_entry_2['name_len'] = self.str2int_le(self.image[offset:offset+1])

            offset += 1
            self.ext4_dir_entry_2['file_type'] = self.str2int_le(self.image[offset:offset+1])

            offset += 1
            self.ext4_dir_entry_2['name'] = self.image[offset:offset+self.ext4_dir_entry_2['name_len']]

        return rec_len

    #
    # Parse Ext4 journal
    #
    def parse_ext4_journal(self, inode_index):
        pass

        if is_pr_verb is True:
            self.print_ext4_journal_info(inode_index)

    #
    # Parse Ext4 directory entries
    #
    def parse_ext4_dir_entry(self, inode_index):
        offset = ((self.ext4_extent['ee_start_hi'] << 32) + self.ext4_extent['ee_start_lo']) * EXT4_BLOCK_SZ
        length = self.ext4_extent['ee_len'] * EXT4_BLOCK_SZ

        i = 0
        while i < length:
            dent_len = self.parse_ext4_dir_entry_internal(offset + i)

            if is_pr_verb is True:
                if (self.ext4_inode_table['i_mode'] & 0xF000) == EXT4_INODE_MODE['S_IFDIR']:
                    if self.ext4_inode_table['i_flags'] & EXT4_INODE_FLAGS['EXT4_INDEX_FL'] != 0:
                        if self.dx_root['dot_inode'] != 0:
                            self.print_ext4_htree_dir_entry_info(inode_index)
                    else:
                        if self.ext4_dir_entry_2['inode'] != 0:
                            self.print_ext4_linear_dir_entry_info(inode_index)

            i += dent_len

    #
    # Parse Ext4 inode in inode table
    #
    def parse_ext4_bg_inode(self, bg_num):
        offset = ((self.ext4_block_group_desc['bg_inode_table_hi'] << 32) + self.ext4_block_group_desc['bg_inode_table_lo']) * EXT4_BLOCK_SZ

        length = self.ext4_super_block['s_inodes_per_group'] - ((self.ext4_block_group_desc['bg_free_inodes_count_hi'] << 32) + self.ext4_block_group_desc['bg_free_inodes_count_lo'])

        for i in range(0, length, 1):
            inode_index = (bg_num * self.ext4_super_block['s_inodes_per_group']) + i

            self.parse_ext4_bg_inode_internal(offset + i * self.ext4_super_block['s_inode_size'])

            #
            # Parse Ext4 extended attributes, especially for ACLs
            #
            self.parse_ext4_xattr(offset + EXT4_INODE_ENTRY_SZ + self.ext4_inode_table['i_extra_isize'] + i * self.ext4_super_block['s_inode_size'])

            #
            # Print Ext4 inode info in inode table
            #
            if is_pr_verb is True:
                if self.ext4_extent_header['eh_magic'] == EXT4_EXTENT_TREE_MAGIC:
                    self.print_ext4_bg_inode_info(inode_index)

            #
            # Parse Ext4 directory entries, journal inode igored
            #
            if self.ext4_extent_header['eh_magic'] == EXT4_EXTENT_TREE_MAGIC and self.ext4_extent_header['eh_depth'] == 0:
                if (inode_index + 1) == EXT4_JOURNAL_INO:
                    self.parse_ext4_journal(inode_index)
                else:
                    self.parse_ext4_dir_entry(inode_index)

    #
    # Parse Ext4 block group descriptor
    #
    def parse_ext4_bg_desc(self, bg_num):
        blocks_per_group = self.ext4_super_block['s_blocks_per_group']

        if self.is_ext4_bg_has_sb(bg_num) is True:
            if bg_num == 0:
                #
                # Offset = Super Block Size (Group 0 Padding is included)
                #
                offset = self.get_sb_blocks() * EXT4_BLOCK_SZ
            else:
                #
                # Offset = Super Block Size
                #
                offset = (bg_num * blocks_per_group + self.get_sb_blocks()) * EXT4_BLOCK_SZ
        else:
            offset = bg_num * blocks_per_group * EXT4_BLOCK_SZ

        bg_count = self.get_bg_count()

        for i in range(0, bg_count, 1):
            self.parse_ext4_bg_desc_internal(offset + i * self.ext4_super_block['s_desc_size'])

            #
            # Print Ext4 block group descriptor info according to block group #0
            #
            self.print_ext4_bg_desc_info(i)

            #
            # Parse Ext4 inode in inode table
            #
            self.parse_ext4_bg_inode(i)

    #
    # Parse Ext4 block group
    #
    def parse_ext4_bg(self):
        bg_count = self.get_bg_count()

        for i in range(0, bg_count, 1):
            #
            # Parse Ext4 block group descriptor according to block group #0
            #
            if i == 0:
                self.parse_ext4_bg_desc(i)

    #
    # Print Ext4 super block info
    #
    def print_ext4_sb_info(self):
        t = lambda x : x != 0 and time.ctime(x) or "n/a"
        s = lambda x : x == "" and "n/a" or x

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
        print("Mount time                     : " + t(self.ext4_super_block['s_mtime']))
        print("Write time                     : " + t(self.ext4_super_block['s_wtime']))
        print("Mount count                    : " + str(self.ext4_super_block['s_mnt_count']))
        print("Maximum mount count            : " + str(self.ext4_super_block['s_max_mnt_count']))
        print("Magic signature                : 0x%X" % self.ext4_super_block['s_magic'])

        state = ""
        for k, v in EXT4_STATE.items():
            if v == self.ext4_super_block['s_state']:
                state = k
                break
        state = s(state)
        print("File system state              : " + state)

        errors = ""
        for k, v in EXT4_ERRORS.items():
            if v == self.ext4_super_block['s_errors']:
                errors = k
                break
        errors = s(errors)
        print("Errors behaviour               : " + errors)

        print("Minor revision level           : " + str(self.ext4_super_block['s_minor_rev_level']))
        print("Last checked                   : " + str(self.ext4_super_block['s_lastcheck']))
        print("Check interval                 : " + str(self.ext4_super_block['s_checkinterval']))

        creator_os = ""
        for k, v in EXT4_OS.items():
            if v == self.ext4_super_block['s_creator_os']:
                creator_os = k
                break
        creator_os = s(creator_os)
        print("OS type                        : " + creator_os)

        rev_level = ""
        for k, v in EXT4_REV_LEVEL.items():
            if v == self.ext4_super_block['s_rev_level']:
                rev_level = k
                break
        rev_level = s(rev_level)
        print("Revision level                 : " + rev_level)

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
        feature_compat = s(feature_compat)
        print("Compatible feature          : " + feature_compat)

        feature_incompat = ""
        for k, v in EXT4_FEATURE_INCOMPAT.items():
            if (v & self.ext4_super_block['s_feature_incompat']) != 0:
                feature_incompat += k + " "
        feature_incompat = s(feature_incompat)
        print("Incompatible feature        : " + feature_incompat)

        feature_ro_compat = ""
        for k, v in EXT4_FEATURE_RO_COMPAT.items():
            if (v & self.ext4_super_block['s_feature_ro_compat']) != 0:
                feature_ro_compat += k + " "
        feature_ro_compat = s(feature_ro_compat)
        print("Readonly-compatible feature : " + feature_ro_compat)

        print("UUID                        : %x" % self.ext4_super_block['s_uuid'])
        print("Volume name                 : " + s(self.ext4_super_block['s_volume_name']))
        print("Last mounted on             : " + s(self.ext4_super_block['s_last_mounted']))
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

        def_hash_version = ""
        for k, v in EXT4_HASH_VERSION.items():
            if v == self.ext4_super_block['s_def_hash_version']:
                def_hash_version = k
                break
        def_hash_version = s(def_hash_version)
        print("Default hash version for dirs hashes : " + def_hash_version)

        print("Reserved char padding                : " + str(self.ext4_super_block['s_reserved_char_pad']))
        print("Group descriptors size               : " + str(self.ext4_super_block['s_desc_size']))

        default_mount_opts = ""
        for k, v in EXT4_DEFAULT_MOUNT_OPTS.items():
            if (v & self.ext4_super_block['s_default_mount_opts']) != 0:
                default_mount_opts += k + " "
        default_mount_opts = s(default_mount_opts)
        print("Default mount options                : " + default_mount_opts)

        print("First metablock block group          : " + str(self.ext4_super_block['s_first_meta_bg']))
        print("Filesystem-created time              : " + t(self.ext4_super_block['s_mkfs_time']))
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
        misc_flags = s(misc_flags)
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
        s = lambda x : x == "" and "n/a" or x

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
        bg_flags = s(bg_flags)
        print("Block group flags         : " + bg_flags)

        print("Exclusion bitmap at       : " + str((self.ext4_block_group_desc['bg_exclude_bitmap_hi'] << 32) + self.ext4_block_group_desc['bg_exclude_bitmap_lo']))
        print("Unused inode count        : " + str((self.ext4_block_group_desc['bg_itable_unused_hi'] << 32) + self.ext4_block_group_desc['bg_itable_unused_lo']))
        print("Group descriptor checksum : " + str(self.ext4_block_group_desc['bg_checksum']))

    #
    # Print Ext4 inode info in inode table
    #
    def print_ext4_bg_inode_info(self, inode_index):
        t = lambda x : x != 0 and time.ctime(x) or "n/a"
        s = lambda x : x == "" and "n/a" or x

        print("\n----------------------------------------")
        print("EXT4 INODE #%d INFO\n" % (inode_index + 1))

        i_mode_val = self.ext4_inode_table['i_mode']
        i_mode_mutually_exclusive = i_mode_val & 0xF000
        i_mode_str = ""
        for k, v in EXT4_INODE_MODE.items():
            if v == i_mode_mutually_exclusive:
                i_mode_str = k
                break
        if i_mode_str != "":
            i_mode_str += " "
        i_mode_val &= 0xFFF

        for k, v in EXT4_INODE_MODE.items():
            if (v & i_mode_val) != 0:
                i_mode_str += k + " "
        i_mode_str = s(i_mode_str)
        print("File mode                      : " + i_mode_str)

        print("UID                            : " + str((self.ext4_inode_table['l_i_uid_high'] << 32) + self.ext4_inode_table['i_uid']))
        print("File size                      : " + str((self.ext4_inode_table['i_size_high'] << 32) + self.ext4_inode_table['i_size_lo']))
        print("File access time               : " + t(self.ext4_inode_table['i_atime']))
        print("File change time               : " + t(self.ext4_inode_table['i_ctime']))
        print("File modification time         : " + t(self.ext4_inode_table['i_mtime']))
        print("File deletion time             : " + t(self.ext4_inode_table['i_dtime']))
        print("GID                            : " + str((self.ext4_inode_table['l_i_gid_high'] << 32) + self.ext4_inode_table['i_gid']))
        print("Hard link count                : " + str(self.ext4_inode_table['i_links_count']))
        print("Block count                    : " + str((self.ext4_inode_table['l_i_blocks_high'] << 32) + self.ext4_inode_table['i_blocks_lo']))

        i_flags = ""
        for k, v in EXT4_INODE_FLAGS.items():
            if (v & self.ext4_inode_table['i_flags']) != 0:
                i_flags += k + " "
        i_flags = s(i_flags)
        print("Inode flags                    : " + i_flags)

        print("Version number                 : " + str((self.ext4_inode_table['i_version_hi'] << 32) + self.ext4_inode_table['l_i_version']))

        if self.ext4_super_block['s_feature_incompat'] & EXT4_FEATURE_INCOMPAT['EXT4_FEATURE_INCOMPAT_EXTENTS'] != 0:
            print("Extent tree                      ")
            print("  Header                         ")
            print("    Magic number               : 0x%X" % self.ext4_extent_header['eh_magic'])
            print("    Number of valid entries    : " + str(self.ext4_extent_header['eh_entries']))
            print("    Max number of entries      : " + str(self.ext4_extent_header['eh_max']))
            print("    Depth of extent node       : " + str(self.ext4_extent_header['eh_depth']))
            print("    Generation of the tree     : " + str(self.ext4_extent_header['eh_generation']))

            if self.ext4_extent_header['eh_depth'] > 0:
                print("  Index node                     ")
                print("    File blocks                : " + str(self.ext4_extent_idx['ei_block']))
                print("    Next level node block num  : " + str((self.ext4_extent_idx['ei_leaf_hi'] << 32) + self.ext4_extent_idx['ei_leaf_lo']))
            elif self.ext4_extent_header['eh_depth'] == 0:
                print("  Leaf node                      ")
                print("    First logical blocks num   : " + str(self.ext4_extent['ee_block']))
                print("    Blocks num                 : " + str(self.ext4_extent['ee_len']))
                print("    First Physical blocks num  : " + str((self.ext4_extent['ee_start_hi'] << 32) + self.ext4_extent['ee_start_lo']))
            else:
                pass

        print("File version                   : " + str(self.ext4_inode_table['i_generation']))
        print("Extended attribute block / ACL : " + str((self.ext4_inode_table['l_i_file_acl_high'] << 32) + self.ext4_inode_table['i_file_acl_lo']))
        print("Fragment address (obsolete)    : " + str(self.ext4_inode_table['i_obso_faddr']))
        print("Extra inode size               : " + str(self.ext4_inode_table['i_extra_isize']))
        print("Extra change time              : " + t(self.ext4_inode_table['i_ctime_extra']))
        print("Extra modification time        : " + t(self.ext4_inode_table['i_mtime_extra']))
        print("Extra access time              : " + t(self.ext4_inode_table['i_atime_extra']))
        print("File creation time             : " + t(self.ext4_inode_table['i_crtime']))
        print("Extra file creation time       : " + t(self.ext4_inode_table['i_crtime_extra']))

    #
    # Print Ext4 extended attributes info
    #
    def print_ext4_xattr_info(self):
        pass

    #
    # Print Ext4 linear directory entries info
    #
    def print_ext4_linear_dir_entry_info(self, inode_index):
        s = lambda x : x == "" and "n/a" or x

        print("\n----------------------------------------")
        '''
        print("EXT4 DIRECTORY ENTRY #%d INFO\n" % (inode_index + 1))
        '''

        print("Inode number         : " + str(self.ext4_dir_entry_2['inode']))
        print("Directory entry size : " + str(self.ext4_dir_entry_2['rec_len']))
        print("File name length     : " + str(self.ext4_dir_entry_2['name_len']))

        file_type = ""
        for k, v in EXT4_FILE_TYPE.items():
            if v == self.ext4_dir_entry_2['file_type']:
                file_type = k
                break
        file_type = s(file_type)
        print("File type            : " + file_type)

        print("File name            : " + str(self.ext4_dir_entry_2['name'][0:self.ext4_dir_entry_2['rec_len']]))

    #
    # Print Ext4 hash tree directory entries info
    #
    def print_ext4_htree_dir_entry_info(self, inode_index):
        pass

    #
    # Print Ext4 journal info
    #
    def print_ext4_journal_info(self, inode_index):
        pass

    #
    # Run routine
    #
    def run(self):
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
    # Sanity check for parameters
    #
    if image_file == "":
        print("\nERROR: invalid parameter!\n")
        print_usage()
        sys.exit(1)

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
