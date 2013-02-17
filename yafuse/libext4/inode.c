/**
 * inode.c - inode of Ext4.
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
int32_t ext4_fill_inodes(const struct ext4_super_block *sb, const struct ext4_group_desc_min *bg_desc, int32_t *inodes)
{
  *inodes = sb->s_inodes_per_group - bg_desc->bg_free_inodes_count_lo;

  return 0;
}

int32_t ext4_fill_inode(const struct ext4_super_block *sb, const struct ext4_group_desc_min *bg_desc, int32_t inode_num, struct ext4_inode *inode)
{
  int32_t blk_sz = 0;
  int32_t bg_idx = 0;
  __le64 inode_tbl = 0, offset = 0;
  size_t inode_sz = 0;
  int32_t ret = 0;

  ret = ext4_fill_blk_sz(sb, &blk_sz);
  if (ret != 0) {
    return -1;
  }

  inode_num -= 1;

  bg_idx = inode_num / sb->s_inodes_per_group;

  inode_sz = sizeof(struct ext4_inode);

  if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_64BIT
      && sb->s_desc_size > EXT4_MIN_DESC_SIZE) {
    /*
     * Disused here due to 'struct ext4_group_desc_min' used here,
     * instead of 'struct ext4_group_desc'
     */
#if 0
    inode_tbl = (((__le64)bg_desc[bg_idx].bg_inode_table_hi << 32) | (__le64)bg_desc[bg_idx].bg_inode_table_lo) * blk_sz;
    offset = inode_tbl + (__le64)(inode_num * sb->s_inode_size);
#endif
  } else {
    inode_tbl = bg_desc[bg_idx].bg_inode_table_lo * blk_sz;
    offset = inode_tbl + (inode_num * sb->s_inode_size);
  }

  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  ret = io_fread((uint8_t *)inode, inode_sz);
  if (ret != 0) {
    memset((void *)inode, 0, inode_sz);
    return -1;
  }

  return 0;
}

int32_t ext4_inode_mode_is_dir(const struct ext4_inode *inode, int32_t *status)
{
  if (inode->i_mode & EXT4_INODE_MODE_S_IFDIR) {
    *status = 1;
  } else {
    *status = 0;
  }

  return 0;
}
