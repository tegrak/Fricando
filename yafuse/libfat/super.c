/**
 * super.c - Superblock of FAT.
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
#ifdef HAVE_MATH_H
#include <math.h>
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
#define FAT_TYPE_FAT32  "FAT32"

/*
 * Type Definition
 */

/*
 * Global Variable Definition
 */

/*
 * Function Declaration
 */
static inline int32_t fat_is_valid_sec_sz(uint8_t *sec_sz, uint32_t len);
static inline int32_t fat_is_valid_media(uint32_t media);

/*
 * Function Definition
 */
static inline int32_t fat_is_valid_sec_sz(uint8_t *sec_sz, uint32_t len)
{
  uint32_t val = 0;

  if (len != 2) {
    return 0;
  }

  val = (uint32_t)GET_UNALIGNED_LE16(sec_sz);

  return IS_POWER_OF_2(val) && (val >= SECTOR_SIZE) && (val <= SECTOR_SIZE_MAX);
}

static inline int32_t fat_is_valid_media(uint32_t media)
{
  return (media >= 0xF8) || (media == 0xF0);
}

int32_t fat_fill_sb(struct fat_super_block *sb)
{
  int32_t offset = 0;
  size_t sz = 0;
  int32_t is_fat32_fs = 0;
  int32_t ret = 0;

  /*
   * Fill in FAT boot sector
   */
  offset = 0;
  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  sz = sizeof(struct fat_boot_sector);
  ret = io_fread((uint8_t *)&sb->bs, sz);
  if (ret != 0) {
    memset((void *)&sb->bs, 0, sz);
    return -1;
  }

  if (!fat_is_valid_sec_sz((uint8_t *)sb->bs.sector_size, 2)
      || !IS_POWER_OF_2(sb->bs.sec_per_clus)
      || sb->bs.reserved == 0
      || sb->bs.fats == 0
      || !fat_is_valid_media((uint32_t)sb->bs.media)) {
    return -1;
  }

  ret = fat_is_fat32_fs((const struct fat_super_block *)sb, &is_fat32_fs);
  if (ret != 0) {
    return -1;
  }

  /*
   * Fill in FAT boot bsx
   */
  if (is_fat32_fs) {
    offset = FAT32_BSX_OFFSET;
  } else {
    offset = FAT16_BSX_OFFSET;
  }

  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  sz = sizeof(struct fat_boot_bsx);
  ret = io_fread((uint8_t *)&sb->bb, sz);
  if (ret != 0) {
    memset((void *)&sb->bb, 0, sz);
    return -1;
  }

  if (is_fat32_fs) {
    /*
     * Fill in FAT32 boot fsinfo
     */
    offset = sb->bs.info_sector == 0 ? GET_UNALIGNED_LE16(sb->bs.sector_size) : sb->bs.info_sector * GET_UNALIGNED_LE16(sb->bs.sector_size);

    ret = io_fseek(offset);
    if (ret != 0) {
      return -1;
    }

    sz = sizeof(struct fat_boot_fsinfo);
    ret = io_fread((uint8_t *)&sb->bf, sz);
    if (ret != 0) {
      memset((void *)&sb->bf, 0, sz);
      return -1;
    }

    if (sb->bf.signature1 != FAT_FSINFO_SIG1 || sb->bf.signature2 != FAT_FSINFO_SIG2) {
      return -1;
    }
  }

  return 0;
}

int32_t fat_is_fat32_fs(const struct fat_super_block *sb, int32_t *status)
{
  int32_t ret = 0;

  /*
   * strlen of sb->bb.type[8] is 8
   * strlen of FAT_TYPE_FAT32 is 5
   */
  ret = strncmp((const char *)sb->bb.type, (const char *)FAT_TYPE_FAT32, strlen(FAT_TYPE_FAT32));

  *status = (ret == 0) && (sb->bs.fat_length == 0) && (sb->bs.fat32_length != 0);

  return 0;
}

int32_t fat_fill_clus2sec(const struct fat_super_block *sb, int32_t cluster, int32_t *sector)
{
  int32_t is_fat32_fs = 0;
  int32_t ret = 0;

  ret = fat_is_fat32_fs(sb, &is_fat32_fs);
  if (ret != 0) {
    return -1;
  }

  *sector = (int32_t)sb->bs.reserved + ((int32_t)sb->bs.fats * (int32_t)sb->bs.fat_length);

  if (!is_fat32_fs) {
    *sector += ((int32_t)GET_UNALIGNED_LE16(sb->bs.dir_entries) * sizeof(struct msdos_dir_entry)) / ((int32_t)GET_UNALIGNED_LE16(sb->bs.sector_size));
  }

  *sector += (cluster - FAT_START_ENT) * sb->bs.sec_per_clus;

  return 0;
}
