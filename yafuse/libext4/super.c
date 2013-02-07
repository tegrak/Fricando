/**
 * super.c - Superblock of Ext4.
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
#define EXT4_GROUP_0_PAD_SZ  (1024)

#define EXT4_SUPER_MAGIC  (0xEF53)

/*
 * Type Definition
 */

/*
 * Global Variable Definition
 */

/*
 * Function Declaration
 */
static int32_t ext4_is_power_of(int32_t a, int32_t b);
static int32_t ext4_bg_has_sb(const struct ext4_super_block *sb, int32_t bg_idx);

/*
 * Function Definition
 */
static int32_t ext4_is_power_of(int32_t a, int32_t b)
{
  while (a > b) {
    if (a % b) {
      return 0;
    }
    a /= b;
  }

  return (a == b) ? 1 : 0;
}

static int32_t ext4_bg_has_sb(const struct ext4_super_block *sb, int32_t bg_idx)
{
  if (!(sb->s_feature_ro_compat & EXT4_FEATURE_RO_COMPAT_SPARSE_SUPER)) {
    return 1;
  }

  if (bg_idx == 0 || bg_idx == 1) {
    return 1;
  }

  if (ext4_is_power_of(bg_idx, 3) || ext4_is_power_of(bg_idx, 5) || ext4_is_power_of(bg_idx, 7)) {
    return 1;
  }

  return 0;
}

int32_t ext4_fill_sb(struct ext4_super_block *sb)
{
  int32_t offset = 0, sb_sz = 0;
  int32_t ret = 0;

  offset = EXT4_GROUP_0_PAD_SZ;
  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  /*
   * Fill in Ext4 superblock
   * default size of superblock is 1024 bytes
   */
  sb_sz = sizeof(struct ext4_super_block);
  ret = io_fread((uint8_t *)sb, sb_sz);
  if (ret != 0) {
    memset((void *)sb, 0, sb_sz);
    return -1;
  }

  if (sb->s_magic != EXT4_SUPER_MAGIC) {
    return -1;
  }

  return 0;
}

int32_t ext4_fill_blk_sz(const struct ext4_super_block *sb, int32_t *blk_sz)
{
  *blk_sz = (int32_t)pow((double)2, (double)(10 + sb->s_log_block_size));

  return 0;
}

int32_t ext4_fill_bg_groups(const struct ext4_super_block *sb, int32_t *bg_groups)
{
  __le64 blocks_cnt = 0;
  int32_t groups = 0;

  blocks_cnt = ((__le64)sb->s_blocks_count_hi << 32) | (__le64)sb->s_blocks_count_lo;

  groups = DIV_ROUND_UP(blocks_cnt - sb->s_first_data_block, sb->s_blocks_per_group);

  *bg_groups = groups;

  return 0;
}

int32_t ext4_fill_bg_desc(const struct ext4_super_block *sb, int32_t bg_groups, struct ext4_group_desc_min *bg_desc)
{
  int32_t blk_sz = 0;
  int32_t start_blk = 0;
  int32_t sb_blk = 0;
  int32_t i = 0, j = 0;
  int32_t ret = 0;

  ret = ext4_fill_blk_sz(sb, &blk_sz);
  if (ret != 0) {
    return -1;
  }

  for (i = 0; i < bg_groups; ++i) {
    start_blk = sb->s_first_data_block + (i * sb->s_blocks_per_group);

    /*
     * If group has superblock, then block group descriptor exits.
     * offset = 1 block (superblock) or 0 block (no superblock)
     */
    if (ext4_bg_has_sb(sb, i)) {
      sb_blk = 1;

      ret = io_fseek((start_blk + sb_blk) * blk_sz);
      if (ret != 0) {
        return -1;
      }

      for (j = 0; j < bg_groups; ++j) {
        ret = io_fread((uint8_t *)&bg_desc[j], sb->s_desc_size);
        if (ret != 0) {
          memset((void *)&bg_desc[j], 0, sb->s_desc_size);
          return -1;
        }
      }

      break;
    }
  }

  return 0;
}
