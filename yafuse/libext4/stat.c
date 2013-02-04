/**
 * stat.c - Show status of Ext4.
 *
 * Copyright (c) 2013-2014 angersax@gmail.com
 *
 * This program/include file is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as published
 * by the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program/include file is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty
 * of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program (in the main directory of the NTFS-3G
 * distribution in the file COPYING); if not, write to the Free Software
 * Foundation,Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef HAVE_STDIO_H
#include <stdio.h>
#endif
#ifdef HAVE_ERRNO_H
#include <errno.h>
#endif
#ifdef HAVE_STDLIB_H
#include <stdlib.h>
#endif
#ifdef HAVE_STDINT_H
#include <stdint.h>
#endif
#ifdef HAVE_STRING_H
#include <string.h>
#endif
#ifdef HAVE_MATH_H
#include <math.h>
#endif
#ifdef HAVE_TIME_H
#include <time.h>
#endif

#ifdef DEBUG
// Add code here
#endif

#include "include/debug.h"
#include "include/types.h"
#include "include/libext4/ext4.h"
#include "include/libext4/ext4_extents.h"
#include "include/libext4/ext4_jbd2.h"
#include "include/libext4/jbd2.h"
#include "include/libext4/libext4.h"
#include "include/libio/io.h"

/*
 * Macro Definition
 */
#define EXT4_DUMMY_STR  "<none>"
/*
 * Type Definition
 */

/*
 * Global Variable Definition
 */

/*
 * Function Declaration
 */

/*
 * Function Definition
 */
void ext4_show_stats(const struct ext4_super_block *sb)
{
  int32_t i = 0;
  const char *str = NULL;
  time_t tm = 0;

  fprintf(stdout, "Total inode count              : %u\n", sb->s_inodes_count);
  fprintf(stdout, "Total block count              : %llu\n", ((__le64)sb->s_blocks_count_hi << 32) + (__le64)sb->s_blocks_count_lo);
  fprintf(stdout, "Reserved block count           : %llu\n", ((__le64)sb->s_r_blocks_count_hi << 32) + (__le64)sb->s_r_blocks_count_lo);
  fprintf(stdout, "Free block count               : %llu\n", ((__le64)sb->s_free_blocks_count_hi << 32) + (__le64)sb->s_free_blocks_count_lo);
  fprintf(stdout, "Free inode count               : %u\n", sb->s_free_inodes_count);
  fprintf(stdout, "First data block               : %u\n", sb->s_first_data_block);
  fprintf(stdout, "Block size                     : %u\n", (uint32_t)pow((double)2, (double)(10 + sb->s_log_block_size)));
  fprintf(stdout, "Fragment size (obsolete)       : %u\n", (uint32_t)pow((double)2, (double)(10 + sb->s_obso_log_frag_size)));
  fprintf(stdout, "Blocks per group               : %u\n", sb->s_blocks_per_group);
  fprintf(stdout, "Fragments per group (obsolete) : %u\n", sb->s_obso_frags_per_group);
  fprintf(stdout, "Inodes per group               : %u\n", sb->s_inodes_per_group);

  fprintf(stdout, "Mount time                     : ");
  if (sb->s_mtime != 0) {
    tm = (time_t)sb->s_mtime;
    fprintf(stdout, "%s", ctime(&tm));
  } else {
    fprintf(stdout, EXT4_DUMMY_STR);
    fprintf(stdout, "\n");
  }

  fprintf(stdout, "Write time                     : ");
  if (sb->s_wtime != 0) {
    tm = (time_t)sb->s_wtime;
    fprintf(stdout, "%s", ctime(&tm));
  } else {
    fprintf(stdout, EXT4_DUMMY_STR);
    fprintf(stdout, "\n");
  }

  fprintf(stdout, "Mount count                    : %u\n", sb->s_mnt_count);
  fprintf(stdout, "Maximum mount count            : %u\n", sb->s_max_mnt_count);
  fprintf(stdout, "Magic signature                : 0x%X\n", sb->s_magic);

  switch (sb->s_state) {
  case EXT4_VALID_FS:
    str = "cleanly umounted";
    break;
  case EXT4_ERROR_FS:
    str = "errors detected";
    break;
  case EXT4_ORPHAN_FS:
    str = "orphans being recovered";
    break;
  default:
    str = EXT4_DUMMY_STR;
    break;
  }
  fprintf(stdout, "File system state              : %s\n", str);

  switch (sb->s_errors) {
  case EXT4_ERRORS_CONTINUE:
    str = "continue";
    break;
  case EXT4_ERRORS_RO:
    str = "remount read-only";
    break;
  case EXT4_ERRORS_PANIC:
    str = "panic";
    break;
  default:
    str = EXT4_DUMMY_STR;
    break;
  }
  fprintf(stdout, "Errors behaviour               : %s\n", str);

  fprintf(stdout, "Minor revision level           : %u\n", sb->s_minor_rev_level);
  fprintf(stdout, "Last checked                   : %u\n", sb->s_lastcheck);
  fprintf(stdout, "Check interval                 : %u\n", sb->s_checkinterval);

  switch (sb->s_creator_os) {
  case EXT4_OS_LINUX:
    str = "Linux";
    break;
  case EXT4_OS_HURD:
    str = "Hurd";
    break;
  case EXT4_OS_MASIX:
    str = "Masix";
    break;
  case EXT4_OS_FREEBSD:
    str = "FreeBSD";
    break;
  case EXT4_OS_LITES:
    str = "Lites";
    break;
  default:
    str = EXT4_DUMMY_STR;
    break;
  }
  fprintf(stdout, "OS type                        : %s\n", str);

  switch (sb->s_rev_level) {
  case EXT4_GOOD_OLD_REV:
    str = "original format";
    break;
  case EXT4_DYNAMIC_REV:
    str = "v2 format w/ dynamic inode sizes";
    break;
  default:
    str = EXT4_DUMMY_STR;
    break;
  }
  fprintf(stdout, "Revision level                 : %s\n", str);

  fprintf(stdout, "Reserved blocks uid            : %u\n", sb->s_def_resuid);
  fprintf(stdout, "Reserved blocks gid            : %u\n", sb->s_def_resgid);

  if (sb->s_rev_level == EXT4_DYNAMIC_REV) {
    fprintf(stdout, "\n");
    fprintf(stdout, "First non-reserved inode    : %u\n", sb->s_first_ino);
    fprintf(stdout, "Inode size                  : %u\n", sb->s_inode_size);
    fprintf(stdout, "Block group number          : %u\n", sb->s_block_group_nr);

    str = NULL;
    fprintf(stdout, "Compatible feature          : ");
    if (sb->s_feature_compat & EXT4_FEATURE_COMPAT_DIR_PREALLOC) {
      str = "directory preallocation";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & EXT4_FEATURE_COMPAT_IMAGIC_INODES) {
      str = "imagic inodes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & EXT4_FEATURE_COMPAT_HAS_JOURNAL) {
      str = "has a journal";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & EXT4_FEATURE_COMPAT_EXT_ATTR) {
      str = "support extended attributes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & EXT4_FEATURE_COMPAT_RESIZE_INODE) {
      str = "has reserved GDT blocks for filesystem expansion";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & EXT4_FEATURE_COMPAT_DIR_INDEX) {
      str = "has directory indices";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & 0x40) {
      str = "lazy BG";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & 0x80) {
      str = "exclude inode";
      fprintf(stdout, "%s, ", str);
    }
    if (str == NULL) {
      fprintf(stdout, EXT4_DUMMY_STR);
    }
    fprintf(stdout, "\n");

    str = NULL;
    fprintf(stdout, "Incompatible feature        : ");
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_COMPRESSION) {
      str = "compression";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_FILETYPE) {
      str = "directory entries record the file type";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_RECOVER) {
      str = "need recovery";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_JOURNAL_DEV) {
      str = "has a separate journal device";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_META_BG) {
      str = "meta block groups";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_EXTENTS) {
      str = "use extents for file";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_64BIT) {
      str = "support size of 2^64 blocks";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_MMP) {
      str = "multiple mount protection";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_FLEX_BG) {
      str = "flexible block groups";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_EA_INODE) {
      str = "support inode with large extended attributes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_DIRDATA) {
      str = "data in directory entry";
      fprintf(stdout, "%s, ", str);
    }
    if (str == NULL) {
      fprintf(stdout, EXT4_DUMMY_STR);
    }
    fprintf(stdout, "\n");

    str = NULL;
    fprintf(stdout, "Readonly-compatible feature : ");
    if (sb->s_feature_ro_compat & EXT4_FEATURE_RO_COMPAT_SPARSE_SUPER) {
      str = "sparse superblocks";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & EXT4_FEATURE_RO_COMPAT_LARGE_FILE) {
      str = "support file greater than 2GiB";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & EXT4_FEATURE_RO_COMPAT_BTREE_DIR) {
      str = "has btree directory";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & EXT4_FEATURE_RO_COMPAT_HUGE_FILE) {
      str = "support huge file";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & EXT4_FEATURE_RO_COMPAT_GDT_CSUM) {
      str = "group descriptors have checksums";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & EXT4_FEATURE_RO_COMPAT_DIR_NLINK) {
      str = "not support old ext3 32,000 subdirectory limit";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & EXT4_FEATURE_RO_COMPAT_EXTRA_ISIZE) {
      str = "support large inodes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & 0x80) {
      str = "has a snapshot";
      fprintf(stdout, "%s, ", str);
    }
    if (str == NULL) {
      fprintf(stdout, EXT4_DUMMY_STR);
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "UUID                        : ");
    for (i = 0; i < 16; ++i) {
      fprintf(stdout, "%x", sb->s_uuid[i]);
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "Volume name                 : ");
    if (sb->s_volume_name[0] == '\0') {
      fprintf(stdout, EXT4_DUMMY_STR);
    } else {
      for (i = 0; i < 16; ++i) {
        fprintf(stdout, "%c", sb->s_volume_name[i]);
      }
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "Last mounted on             : ");
    if (sb->s_last_mounted[0] == '\n') {
      fprintf(stdout, EXT4_DUMMY_STR);
    } else {
      for (i = 0; i < 64; ++i) {
        fprintf(stdout, "%c", sb->s_last_mounted[i]);
      }
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "Bitmap algorithm usage      : %u\n", sb->s_algorithm_usage_bitmap);
  }

  if (sb->s_feature_compat & EXT4_FEATURE_COMPAT_DIR_PREALLOC) {
    fprintf(stdout, "\n");
    fprintf(stdout, "Blocks preallocated for files : %u\n", sb->s_prealloc_blocks);
    fprintf(stdout, "Blocks preallocated for dirs  : %u\n", sb->s_prealloc_dir_blocks);
    fprintf(stdout, "Reserved GDT blocks           : %u\n", sb->s_reserved_gdt_blocks);
  }

  if (sb->s_feature_compat & EXT4_FEATURE_COMPAT_HAS_JOURNAL) {
    fprintf(stdout, "\n");
    fprintf(stdout, "Journal UUID                         : ");
    for (i = 0; i < 16; ++i) {
      fprintf(stdout, "%x", sb->s_journal_uuid[i]);
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "Journal inode                        : %u\n", sb->s_journal_inum);
    fprintf(stdout, "Journal device                       : %u\n", sb->s_journal_dev);
    fprintf(stdout, "Orphaned inodes to delete            : %u\n", sb->s_last_orphan);

    fprintf(stdout, "HTREE hash seed                      : ");
    for (i = 0; i < (4 * 4); ++i) {
      fprintf(stdout, "%x", *((__u8 *)(sb->s_hash_seed) + i));
    }
    fprintf(stdout, "\n");

    switch (sb->s_def_hash_version) {
    case DX_HASH_LEGACY:
      str = "legacy";
      break;
    case DX_HASH_HALF_MD4:
      str = "half MD4";
      break;
    case DX_HASH_TEA:
      str = "tea";
      break;
    case DX_HASH_LEGACY_UNSIGNED:
      str = "unsigned legacy";
      break;
    case DX_HASH_HALF_MD4_UNSIGNED:
      str = "unsigned half MD4";
      break;
    case DX_HASH_TEA_UNSIGNED:
      str = "unsigned tea";
      break;
    default:
      str = EXT4_DUMMY_STR;
      break;
    }
    fprintf(stdout, "Default hash version for dirs hashes : %s\n", str);

    fprintf(stdout, "Reserved char padding                : %u\n", sb->s_reserved_char_pad);
    fprintf(stdout, "Group descriptors size               : %u\n", sb->s_desc_size);

    str = NULL;
    fprintf(stdout, "Default mount options                : ");
    if (sb->s_default_mount_opts & EXT4_DEFM_DEBUG) {
      str = "print debugging info upon (re)mount";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_BSDGROUPS) {
      str = "New files take the gid of the containing directory";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_XATTR_USER) {
      str = "support userspace-provided extended attributes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_ACL) {
      str = "support POSIX access control lists (ACLs)";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_UID16) {
      str = "not support 32-bit UIDs";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_JMODE_DATA) {
      str = "all data and metadata are commited to the journal";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_JMODE_ORDERED) {
      str = "all data are flushed to the disk before metadata are committed to the journal";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_JMODE_WBACK) {
      str = "data ordering is not preserved which may be written after the metadata has been written";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_NOBARRIER) {
      str = "disable write flushes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_BLOCK_VALIDITY) {
      str = "track which blocks in a filesystem are metadata";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_DISCARD) {
      str = "enable DISCARD support";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & EXT4_DEFM_NODELALLOC) {
      str = "disable delayed allocation";
      fprintf(stdout, "%s, ", str);
    }
    if (str == NULL) {
      fprintf(stdout, EXT4_DUMMY_STR);
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "First metablock block group          : %u\n", sb->s_first_meta_bg);

    fprintf(stdout, "Filesystem-created time              : ");
    if (sb->s_mkfs_time != 0) {
      tm = (time_t)sb->s_mkfs_time;
      fprintf(stdout, "%s", ctime(&tm));
    } else {
      fprintf(stdout, EXT4_DUMMY_STR);
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "Journal backup                       : ");
    for (i = 0; i < (17 * 4); ++i) {
      fprintf(stdout, "%x", *((__u8 *)(sb->s_jnl_blocks) + i));
    }
    fprintf(stdout, "\n");
  }

  if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_64BIT) {
    fprintf(stdout, "\n");
    fprintf(stdout, "Required extra isize             : %u\n", sb->s_min_extra_isize);
    fprintf(stdout, "Desired extra isize              : %u\n", sb->s_want_extra_isize);

    str = NULL;
    fprintf(stdout, "Misc flags                       : ");
    if (sb->s_flags & EXT2_FLAGS_SIGNED_HASH) {
      str = "signed directory hash in use";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_flags & EXT2_FLAGS_UNSIGNED_HASH) {
      str = "unsigned directory hash in use";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_flags & EXT2_FLAGS_TEST_FILESYS) {
      str = "to test development code";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_flags & 0x10) {
      str = "is snapshot";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_flags & 0x20) {
      str = "fix snapshot";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_flags & 0x40) {
      str = "fix exclusion";
      fprintf(stdout, "%s, ", str);
    }
    if (str == NULL) {
      fprintf(stdout, EXT4_DUMMY_STR);
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "RAID stride                      : %u\n", sb->s_raid_stride);
    fprintf(stdout, "MMP checking wait time (seconds) : %u\n", sb->s_mmp_interval);
    fprintf(stdout, "MMP blocks                       : %llu\n", sb->s_mmp_block);
    fprintf(stdout, "RAID stripe width                : %u\n", sb->s_raid_stripe_width);
    fprintf(stdout, "Flexible block size              : %u\n", (uint32_t)pow((double)2, (double)sb->s_log_groups_per_flex));
    fprintf(stdout, "Reserved char padding 2          : %u\n", sb->s_reserved_char_pad2);
    fprintf(stdout, "Reserved padding                 : %u\n", sb->s_reserved_pad);
    fprintf(stdout, "KiB writtten                     : %llu\n", sb->s_kbytes_written);
  }
}
