/**
 * extent.c - extent of Ext4.
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
#define DEBUG_LIBEXT4_EXTENT
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
static int32_t ext4_fill_extent_header(const struct ext4_inode *inode, struct ext4_extent_header *ext_hdr);
static int32_t ext4_fill_extent_idx(const struct ext4_inode *inode, int32_t ext_idx_num, struct ext4_extent_idx *ext_idx);

/*
 * Function Definition
 */
static int32_t ext4_fill_extent_header(const struct ext4_inode *inode, struct ext4_extent_header *ext_hdr)
{
  memcpy((void *)ext_hdr, (const void *)inode->i_block, sizeof(struct ext4_extent_header));

  return 0;
}

static int32_t __attribute__((unused)) ext4_fill_extent_idx (const struct ext4_inode *inode, int32_t ext_idx_num, struct ext4_extent_idx *ext_idx)
{
  const uint8_t *ptr = NULL;
  int32_t offset = 0;

  ptr = (const uint8_t *)inode->i_block;

  offset = sizeof(struct ext4_extent_header) + (ext_idx_num * sizeof(struct ext4_extent_idx));

  memcpy((void *)ext_idx, (const void *)(ptr + offset), sizeof(struct ext4_extent_idx));

  return 0;
}

int32_t ext4_fill_extents(const struct ext4_inode *inode, int32_t *extents)
{
  // Add code here

  inode = inode;
  *extents = 1;

  return 0;
}

int32_t ext4_fill_extent(const struct ext4_inode *inode, int32_t extents, struct ext4_extent *extent)
{
  struct ext4_extent_header ext_hdr;
  struct ext4_extent_idx ext_idx __attribute__((unused));
  int32_t i = 0;
  const uint8_t *ptr = NULL;
  int32_t offset = 0;
  int32_t ret = 0;

  memset((void *)&ext_hdr, 0, sizeof(struct ext4_extent_header));

  ret = ext4_fill_extent_header(inode, &ext_hdr);
  if (ret != 0) {
    return -1;
  }

#ifdef DEBUG_LIBEXT4_EXTENT
  ext4_show_extent_header((const struct ext4_extent_header *)&ext_hdr);
#endif

#if 0
  memset((void *)&ext_idx, 0, sizeof(struct ext4_extent_idx));

  ret = ext4_fill_extent_idx(inode, int32_t ext_idx_num, &ext_idx);
  if (ret != 0) {
    return -1;
  }

#ifdef DEBUG_LIBEXT4_EXTENT
  ext4_show_extent_idx((const struct ext4_extent_idx *)&ext_idx);
#endif
#endif

  ptr = (const uint8_t *)inode->i_block;

  for (i = 0; i < extents; ++i) {
    offset = sizeof(struct ext4_extent_header) + (i * sizeof(struct ext4_extent));

    memcpy((void *)&extent[i], (const void *)(ptr + offset), sizeof(struct ext4_extent));

#ifdef DEBUG_LIBEXT4_EXTENT
    ext4_show_extent((const struct ext4_extent *)&extent[i]);
#endif
  }

  return 0;
}
