/**
 * dir.c - directory of Ext4.
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
 * along with this program (in the main directory of the distribution
 * in the file COPYING); if not, write to the Free Software
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
#define DEBUG_LIBEXT4_DIR
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
static int32_t ext4_fill_dentry_linear(const struct ext4_super_block *sb, const struct ext4_extent *ext, uint32_t dentry_offset_rel, struct ext4_dir_entry_2 *dentry);
static int32_t ext4_fill_dentry_htree(const struct ext4_super_block *sb, const struct ext4_extent *ext, int32_t root_num, struct dx_root *root);

/*
 * Function Definition
 */
static int32_t ext4_fill_dentry_linear(const struct ext4_super_block *sb, const struct ext4_extent *ext, uint32_t dentry_offset_rel, struct ext4_dir_entry_2 *dentry)
{
  int32_t blk_sz = 0;
  __le64 offset = 0;
  uint32_t rec_len = 0;
  int32_t ret = 0;

  ret = ext4_fill_blk_sz(sb, &blk_sz);
  if (ret != 0) {
    return -1;
  }

  offset = (((__le64)ext->ee_start_hi << 32) | (__le64)ext->ee_start_lo) * blk_sz + (__le64)dentry_offset_rel;

  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  ret = io_fread((uint8_t *)&dentry->inode, sizeof(__le32));
  if (ret != 0) {
    return -1;
  }

  ret = io_fread((uint8_t *)&dentry->rec_len, sizeof(__le16));
  if (ret != 0) {
    return -1;
  }

  rec_len = dentry->rec_len <= sizeof(struct ext4_dir_entry_2) ? dentry->rec_len : sizeof(struct ext4_dir_entry_2);

  ret = io_fread((uint8_t *)dentry + sizeof(__le32) + sizeof(__le16), rec_len - sizeof(__le32) - sizeof(__le16));
  if (ret != 0) {
    return -1;
  }

  return 0;
}

static int32_t __attribute__((unused)) ext4_fill_dentry_htree(const struct ext4_super_block *sb, const struct ext4_extent *ext, int32_t root_num, struct dx_root *root)
{
  // Add code here

  sb = sb;
  ext = ext;
  root_num = root_num;
  root = root;

  return -1;
}

int32_t ext4_fill_dentries(const struct ext4_super_block *sb, const struct ext4_extent *ext, int32_t *dentries)
{
  int32_t blk_sz = 0;
  __le64 offset = 0;
  int32_t i = 0;
  struct ext4_dir_entry_2 dentry;
  int32_t ret = 0;

  ret = ext4_fill_blk_sz(sb, &blk_sz);
  if (ret != 0) {
    return -1;
  }

  offset = (((__le64)ext->ee_start_hi << 32) | (__le64)ext->ee_start_lo) * blk_sz;

  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  ret = io_fread((uint8_t *)&dentry.inode, sizeof(__le32));
  if (ret != 0) {
    return -1;
  }

  ret = io_fread((uint8_t *)&dentry.rec_len, sizeof(__le16));
  if (ret != 0) {
    return -1;
  }

  while (dentry.inode != EXT4_UNUSED_INO) {
    ++i;

    offset += (__le64)(dentry.rec_len <= sizeof(struct ext4_dir_entry_2) ? dentry.rec_len : sizeof(struct ext4_dir_entry_2));

    ret = io_fseek(offset);
    if (ret != 0) {
      return -1;
    }

    ret = io_fread((uint8_t *)&dentry.inode, sizeof(__le32));
    if (ret != 0) {
      return -1;
    }

    ret = io_fread((uint8_t *)&dentry.rec_len, sizeof(__le16));
    if (ret != 0) {
      return -1;
    }
  }

  *dentries = i;

  return 0;
}

int32_t ext4_fill_dentry(const struct ext4_super_block *sb, const struct ext4_extent *ext, int32_t dentries, struct ext4_dir_entry_2 *dentry)
{
  uint32_t dentry_offset_rel = 0;
  int32_t i = 0;
  int32_t ret = 0;

  for (i = 0, dentry_offset_rel = 0; i < dentries; ++i) {
    ret = ext4_fill_dentry_linear(sb, ext, dentry_offset_rel, &dentry[i]);
    if (ret != 0) {
      return -1;
    }

    dentry_offset_rel += dentry[i].rec_len <= sizeof(struct ext4_dir_entry_2) ? dentry[i].rec_len : sizeof(struct ext4_dir_entry_2);

#ifdef DEBUG_LIBEXT4_DIR
    ext4_show_dentry_linear((const struct ext4_dir_entry_2 *)&dentry[i]);
#endif
  }

  return 0;
}
