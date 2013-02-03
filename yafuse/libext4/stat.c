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
void ext4_show_stats(struct ext4_super_block *sb)
{
  int32_t i = 0;
  const char *str = NULL;

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
    fprintf(stdout, "%u", sb->s_mtime);
  } else {
    fprintf(stdout, EXT4_DUMMY_STR);
  }
  fprintf(stdout, "\n");

  fprintf(stdout, "Write time                     : ");
  if (sb->s_wtime != 0) {
    fprintf(stdout, "%u", sb->s_wtime);
  } else {
    fprintf(stdout, EXT4_DUMMY_STR);
  }
  fprintf(stdout, "\n");

  fprintf(stdout, "Mount count                    : %u\n", sb->s_mnt_count);
  fprintf(stdout, "Maximum mount count            : %u\n", sb->s_max_mnt_count);
  fprintf(stdout, "Magic signature                : 0x%X\n", sb->s_magic);

  switch (sb->s_state) {
  case 1:
    str = "cleanly umounted";
    break;
  case 2:
    str = "errors detected";
    break;
  case 4:
    str = "orphans being recovered";
    break;
  default:
    str = EXT4_DUMMY_STR;
    break;
  }
  fprintf(stdout, "File system state              : %s\n", str);

  switch (sb->s_errors) {
  case 1:
    str = "continue";
    break;
  case 2:
    str = "remount read-only";
    break;
  case 3:
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
  case 0:
    str = "Linux";
    break;
  case 1:
    str = "Hurd";
    break;
  case 2:
    str = "Masix";
    break;
  case 3:
    str = "FreeBSD";
    break;
  case 4:
    str = "Lites";
    break;
  default:
    str = EXT4_DUMMY_STR;
    break;
  }
  fprintf(stdout, "OS type                        : %s\n", str);

  switch (sb->s_rev_level) {
  case 0:
    str = "original format";
    break;
  case 1:
    str = "v2 format w/ dynamic inode sizes";
    break;
  default:
    str = EXT4_DUMMY_STR;
    break;
  }
  fprintf(stdout, "Revision level                 : %s\n", str);

  fprintf(stdout, "Reserved blocks uid            : %u\n", sb->s_def_resuid);
  fprintf(stdout, "Reserved blocks gid            : %u\n", sb->s_def_resgid);

  if (sb->s_rev_level == 1) {
    fprintf(stdout, "\n");
    fprintf(stdout, "First non-reserved inode    : %u\n", sb->s_first_ino);
    fprintf(stdout, "Inode size                  : %u\n", sb->s_inode_size);
    fprintf(stdout, "Block group number          : %u\n", sb->s_block_group_nr);

    str = NULL;
    fprintf(stdout, "Compatible feature          : ");
    if (sb->s_feature_compat & 0x01) {
      str = "directory preallocation";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & 0x02) {
      str = "imagic inodes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & 0x04) {
      str = "has a journal";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & 0x08) {
      str = "support extended attributes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & 0x10) {
      str = "has reserved GDT blocks for filesystem expansion";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_compat & 0x20) {
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
    if (sb->s_feature_incompat & 0x0001) {
      str = "compression";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0002) {
      str = "directory entries record the file type";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0004) {
      str = "need recovery";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0008) {
      str = "has a separate journal device";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0010) {
      str = "meta block groups";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0040) {
      str = "use extents for file";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0080) {
      str = "support size of 2^64 blocks";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0100) {
      str = "multiple mount protection";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0200) {
      str = "flexible block groups";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x0400) {
      str = "support inode with large extended attributes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_incompat & 0x1000) {
      str = "data in directory entry";
      fprintf(stdout, "%s, ", str);
    }
    if (str == NULL) {
      fprintf(stdout, EXT4_DUMMY_STR);
    }
    fprintf(stdout, "\n");

    str = NULL;
    fprintf(stdout, "Readonly-compatible feature : ");
    if (sb->s_feature_ro_compat & 0x01) {
      str = "sparse superblocks";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & 0x02) {
      str = "support file greater than 2GiB";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & 0x04) {
      str = "has btree directory";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & 0x08) {
      str = "support huge file";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & 0x10) {
      str = "group descriptors have checksums";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & 0x20) {
      str = "not support old ext3 32,000 subdirectory limit";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_feature_ro_compat & 0x40) {
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

    fprintf(stdout, "UUID                        : 0x");
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

  if (sb->s_feature_compat & 0x01) {
    fprintf(stdout, "\n");
    fprintf(stdout, "Blocks preallocated for files : %u\n", sb->s_prealloc_blocks);
    fprintf(stdout, "Blocks preallocated for dirs  : %u\n", sb->s_prealloc_dir_blocks);
    fprintf(stdout, "Reserved GDT blocks           : %u\n", sb->s_reserved_gdt_blocks);
  }

  if (sb->s_feature_compat & 0x04) {
    fprintf(stdout, "\n");
    fprintf(stdout, "Journal UUID                         : 0x");
    for (i = 0; i < 16; ++i) {
      fprintf(stdout, "%x", sb->s_journal_uuid[i]);
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "Journal inode                        : %u\n", sb->s_journal_inum);
    fprintf(stdout, "Journal device                       : %u\n", sb->s_journal_dev);
    fprintf(stdout, "Orphaned inodes to delete            : %u\n", sb->s_last_orphan);

    fprintf(stdout, "HTREE hash seed                      : 0x");
    for (i = 0; i < (4 * 4); ++i) {
      fprintf(stdout, "%x", *((__u8 *)(sb->s_hash_seed) + i));
    }
    fprintf(stdout, "\n");

    switch (sb->s_def_hash_version) {
    case 0:
      str = "legacy";
      break;
    case 1:
      str = "half MD4";
      break;
    case 2:
      str = "tea";
      break;
    case 3:
      str = "unsigned legacy";
      break;
    case 4:
      str = "unsigned half MD4";
      break;
    case 5:
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
    if (sb->s_default_mount_opts & 0x0001) {
      str = "print debugging info upon (re)mount";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0002) {
      str = "New files take the gid of the containing directory";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0004) {
      str = "support userspace-provided extended attributes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0008) {
      str = "support POSIX access control lists (ACLs)";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0010) {
      str = "not support 32-bit UIDs";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0020) {
      str = "all data and metadata are commited to the journal";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0040) {
      str = "all data are flushed to the disk before metadata are committed to the journal";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0060) {
      str = "data ordering is not preserved which may be written after the metadata has been written";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0100) {
      str = "disable write flushes";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0200) {
      str = "track which blocks in a filesystem are metadata";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0400) {
      str = "enable DISCARD support";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_default_mount_opts & 0x0800) {
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
      fprintf(stdout, "%u", sb->s_mkfs_time);
    } else {
      fprintf(stdout, EXT4_DUMMY_STR);
    }
    fprintf(stdout, "\n");

    fprintf(stdout, "Journal backup                       : 0x");
    for (i = 0; i < (17 * 4); ++i) {
      fprintf(stdout, "%x", *((__u8 *)(sb->s_jnl_blocks) + i));
    }
    fprintf(stdout, "\n");
  }

  if (sb->s_feature_incompat & 0x0080) {
    fprintf(stdout, "\n");
    fprintf(stdout, "Required extra isize             : %u\n", sb->s_min_extra_isize);
    fprintf(stdout, "Desired extra isize              : %u\n", sb->s_want_extra_isize);

    str = NULL;
    fprintf(stdout, "Misc flags                       : ");
    if (sb->s_flags & 0x01) {
      str = "signed directory hash in use";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_flags & 0x02) {
      str = "unsigned directory hash in use";
      fprintf(stdout, "%s, ", str);
    }
    if (sb->s_flags & 0x04) {
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
