/**
 * dir.c - directory of FAT.
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
// Add code here
#endif

#include "include/debug.h"
#include "include/types.h"
#include "include/libfat/msdos_fs.h"
#include "include/libfat/libfat.h"
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
static int32_t fat_fill_root_dent_sec(const struct fat_super_block *sb, int32_t *sector);

/*
 * Function Definition
 */
static int32_t fat_fill_root_dent_sec(const struct fat_super_block *sb, int32_t *sector)
{
  *sector = (int32_t)sb->bs.reserved + ((int32_t)sb->bs.fats * (int32_t)sb->bs.fat_length);

  return 0;
}

int32_t fat_fill_root_dentries(const struct fat_super_block *sb, int32_t *dentries)
{
  int32_t root_den_sec = 0;
  int32_t offset = 0;
  struct msdos_dir_entry dentry;
  int32_t sz = 0;
  int32_t i = 0;
  int32_t ret = 0;

  ret = fat_fill_root_dent_sec(sb, &root_den_sec);
  if (ret != 0) {
    return -1;
  }

  offset = root_den_sec * (int32_t)GET_UNALIGNED_LE16(sb->bs.sector_size);
  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  sz = sizeof(struct msdos_dir_entry);

  /*
   * Read FAT dentry of '.'
   */
  ret = io_fread((uint8_t *)&dentry, sz);
  if (ret != 0) {
    return -1;
  }

  while (dentry.name[0] != '\0') {
    ++i;

    ret = io_fread((uint8_t *)&dentry, sz);
    if (ret != 0) {
      return -1;
    }
  }

  *dentries = i;

  return 0;
}

int32_t fat_fill_root_dentry(const struct fat_super_block *sb, int32_t dentries, struct msdos_dir_entry *dentry)
{
  int32_t root_den_sec = 0;
  int32_t offset = 0;
  int32_t sz = 0;
  int32_t i = 0;
  int32_t ret = 0;

  ret = fat_fill_root_dent_sec(sb, &root_den_sec);
  if (ret != 0) {
    return -1;
  }

  offset = root_den_sec * (int32_t)GET_UNALIGNED_LE16(sb->bs.sector_size);
  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  sz = sizeof(struct msdos_dir_entry);

  for (i = 0; i < dentries; ++i) {
    ret = io_fread((uint8_t *)&dentry[i], sz);
    if (ret != 0) {
      break;
    }
  }

  return ret;
}

int32_t fat_fill_dentries(const struct fat_super_block *sb, int32_t cluster, int32_t *dentries)
{
  int32_t sector = 0;
  int32_t offset = 0;
  struct msdos_dir_entry dentry;
  int32_t sz = 0;
  int32_t i = 0;
  int32_t ret = 0;

  ret = fat_fill_clus2sec(sb, cluster, &sector);
  if (ret != 0) {
    return -1;
  }

  offset = sector * (int32_t)GET_UNALIGNED_LE16(sb->bs.sector_size);
  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  sz = sizeof(struct msdos_dir_entry);

  /*
   * Read FAT dentry of '.'
   */
  ret = io_fread((uint8_t *)&dentry, sz);
  if (ret != 0) {
    return -1;
  }

  while (dentry.name[0] != '\0') {
    ++i;

    ret = io_fread((uint8_t *)&dentry, sz);
    if (ret != 0) {
      return -1;
    }
  }

  *dentries = i;

  return 0;
}

int32_t fat_fill_dentry(const struct fat_super_block *sb, int32_t cluster, int32_t dentries, struct msdos_dir_entry *dentry)
{
  int32_t sector = 0;
  int32_t offset = 0;
  int32_t sz = 0;
  int32_t i = 0;
  int32_t ret = 0;

  ret = fat_fill_clus2sec(sb, cluster, &sector);
  if (ret != 0) {
    return -1;
  }

  offset = sector * (int32_t)GET_UNALIGNED_LE16(sb->bs.sector_size);
  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  sz = sizeof(struct msdos_dir_entry);

  for (i = 0; i < dentries; ++i) {
    ret = io_fread((uint8_t *)&dentry[i], sz);
    if (ret != 0) {
      break;
    }
  }

  return ret;
}

int32_t fat_fill_dent_start(const struct fat_super_block *sb, const struct msdos_dir_entry *dentry, int32_t *start_cluster)
{
  int32_t is_fat32_fs = 0;
  int32_t ret = 0;

  ret = fat_is_fat32_fs(sb, &is_fat32_fs);
  if (ret != 0) {
    return -1;
  }

  if (is_fat32_fs) {
    *start_cluster = ((int32_t)dentry->starthi << 16) | (int32_t)dentry->start;
  } else {
    *start_cluster = (int32_t)dentry->start;
  }

  return 0;
}
