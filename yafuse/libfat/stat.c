/**
 * stat.c - Show status of FAT.
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
#ifdef HAVE_TIME_H
#include <time.h>
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
#define FAT_DUMMY_STR  "<none>"

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
void fat_show_stats(const struct fat_super_block *sb)
{
  int32_t i = 0;
  int32_t is_fat32_fs = 0;
  uint32_t vol_id = 0;
  int32_t ret = 0;

  /*
   * Show FAT boot sector
   */
  fprintf(stdout, "System ID                : ");
  for (i = 0; i < 8; ++i) {
    fprintf(stdout, "%c", sb->bs.system_id[i]);
  }
  fprintf(stdout, "\n");

  fprintf(stdout, "Sector size              : %u\n", GET_UNALIGNED_LE16(sb->bs.sector_size));
  fprintf(stdout, "Sector per cluster       : %u\n", sb->bs.sec_per_clus);
  fprintf(stdout, "Sector reserved          : %u\n", sb->bs.reserved);
  fprintf(stdout, "FAT copies number        : %u\n", sb->bs.fats);
  fprintf(stdout, "Max root dentries        : %u\n", GET_UNALIGNED_LE16(sb->bs.dir_entries));
  fprintf(stdout, "Small 32MB sector number : %u\n", GET_UNALIGNED_LE16(sb->bs.sectors));
  fprintf(stdout, "Media descriptor         : 0x%X\n", sb->bs.media);
  fprintf(stdout, "Sector per FAT           : %u\n", sb->bs.fat_length);
  fprintf(stdout, "Sector per track         : %u\n", sb->bs.secs_track);
  fprintf(stdout, "Head number              : %u\n", sb->bs.heads);
  fprintf(stdout, "Hidden sector number     : %u\n", sb->bs.hidden);
  fprintf(stdout, "Total sector number      : %u\n", sb->bs.total_sect);

  ret = fat_is_fat32_fs(sb, &is_fat32_fs);
  if (ret != 0) {
    return;
  }

  if (is_fat32_fs) {
    fprintf(stdout, "Sector per FAT32         : %u\n", sb->bs.fat32_length);
    fprintf(stdout, "Version number           : %u\n", GET_UNALIGNED_LE16(sb->bs.version));
    fprintf(stdout, "Root cluster             : %u\n", sb->bs.root_cluster);
    fprintf(stdout, "FS info sector number    : %u\n", sb->bs.info_sector);
    fprintf(stdout, "Backup boot sector       : %u\n", sb->bs.backup_boot);
  }

  fprintf(stdout, "\n");

  /*
   * Show FAT boot bsx
   */
  fprintf(stdout, "Logical drive number : %u\n", sb->bb.drive);
  fprintf(stdout, "Ext signature        : 0x%X\n", sb->bb.signature);


  vol_id = (((uint32_t)sb->bb.vol_id[3] << 24)
            | ((uint32_t)sb->bb.vol_id[2] << 16)
            | ((uint32_t)sb->bb.vol_id[1] << 8)
            | ((uint32_t)sb->bb.vol_id[0]));
  fprintf(stdout, "Serial number        : %u\n", vol_id);

  fprintf(stdout, "Volume name          : ");
  for (i = 0; i < 11; ++i) {
    fprintf(stdout, "%c", sb->bb.vol_label[i]);
  }
  fprintf(stdout, "\n");

  fprintf(stdout, "FAT name             : ");
  for (i = 0; i < 8; ++i) {
    fprintf(stdout, "%c", sb->bb.type[i]);
  }
  fprintf(stdout, "\n");

  /*
   * Show FAT32 boot FS info
   */
  if (is_fat32_fs) {
    fprintf(stdout, "\n");
    fprintf(stdout, "Signature1    : 0x%X\n", sb->bf.signature1);
    fprintf(stdout, "Signature2    : 0x%X\n", sb->bf.signature2);
    fprintf(stdout, "Free clusters : %u\n", sb->bf.free_clusters);
    fprintf(stdout, "Next cluster  : %u\n", sb->bf.next_cluster);
  }
}

void fat_show_dentry(const struct fat_super_block *sb, const struct msdos_dir_entry *dentry)
{
  int32_t i = 0;
  const char *str = NULL;
  int32_t is_fat32_fs = 0;
  uint32_t ctime_h = 0, ctime_m = 0, ctime_s = 0;
  uint32_t cdate_y = 0, cdate_m = 0, cdate_d = 0;
  uint32_t adate_y = 0, adate_m = 0, adate_d = 0;
  uint32_t mtime_h = 0, mtime_m = 0, mtime_s = 0;
  uint32_t mdate_y = 0, mdate_m = 0, mdate_d = 0;
  int32_t ret = 0;

  /*
   * Show FAT directory entry
   */
  fprintf(stdout, "Name                 : ");
  for (i = 0; i < MSDOS_NAME_BASE_LEN; ++i) {
    fprintf(stdout, "%c", dentry->name[i]);
  }
  fprintf(stdout, "\n");

  fprintf(stdout, "Extension            : ");
  if (dentry->name[MSDOS_NAME_BASE_LEN] == '\0' || dentry->name[MSDOS_NAME_BASE_LEN] == 0x20) {
    fprintf(stdout, "%s", FAT_DUMMY_STR);
  } else {
    for (i = 0; i < MSDOS_NAME_EXT_LEN; ++i) {
      fprintf(stdout, "%c", dentry->name[i + MSDOS_NAME_BASE_LEN]);
    }
  }
  fprintf(stdout, "\n");

  str = NULL;
  fprintf(stdout, "File attribute       : ");
  if (dentry->attr & ATTR_RO) {
    str = "read-only";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->attr & ATTR_HIDDEN) {
    str = "hidden";
    fprintf(stdout, "%s, ", str);
  }
  if (dentry->attr & ATTR_SYS) {
    str = "system";
    fprintf(stdout, "%s, ", str);
  }
  if (dentry->attr & ATTR_VOLUME) {
    str = "volume label";
    fprintf(stdout, "%s, ", str);
  }
  if (dentry->attr & ATTR_DIR) {
    str = "directory";
    fprintf(stdout, "%s, ", str);
  }
  if (dentry->attr & ATTR_ARCH) {
    str = "archived";
    fprintf(stdout, "%s, ", str);
  }
  if (dentry->attr == ATTR_NONE) {
    str = FAT_DUMMY_STR;
    fprintf(stdout, "%s", str);
  }
  fprintf(stdout, "\n");

  str = NULL;
  fprintf(stdout, "User attribute       : ");
  if (dentry->lcase & LCASE_READ_REQ_PASS) {
    str = "read requires password";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->lcase & LCASE_WRITE_REQ_PASS) {
    str = "write requires password";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->lcase & LCASE_DEL_REQ_PASS) {
    str = "delete requires password";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->lcase & LCASE_RESERVED) {
    str = "reserved";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->lcase & LCASE_DISABLE_CHKSUM) {
    str = "disable checksums";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->lcase & LCASE_IGNORE_CLOSE_CHKSUM_ERR) {
    str = "ignore close checksum error";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->lcase & LCASE_PARTIAL_CLOSE_DEFAULT) {
    str = "partial close default";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->lcase & LCASE_MODIFY_DEFAULT_OPEN_RULES) {
    str = "modify default open rules";
    fprintf(stdout, "%s, ", str);
  } 
  if (dentry->lcase == LCASE_NONE) {
    str = FAT_DUMMY_STR;
    fprintf(stdout, "%s", str);
  }
  fprintf(stdout, "\n");

  fprintf(stdout, "Time resolution      : %u\n", dentry->ctime_cs);

  ctime_h = (dentry->ctime >> 11) & 0x001F;
  ctime_m = (dentry->ctime >> 5) & 0x003F;
  ctime_s = (dentry->ctime & 0x001F) << 1;
  fprintf(stdout, "Created time         : %u:%u:%u\n", ctime_h, ctime_m, ctime_s);

  cdate_y = ((dentry->cdate >> 9) & 0x007F) + 1980;
  cdate_m = (dentry->cdate >> 5) & 0x000F;
  cdate_d = dentry->cdate & 0x001F;
  fprintf(stdout, "Created date         : %u-%u-%u\n", cdate_y, cdate_m, cdate_d);

  adate_y = ((dentry->adate >> 9) & 0x007F) + 1980;
  adate_m = (dentry->adate >> 5) & 0x000F;
  adate_d = dentry->adate & 0x001F;
  fprintf(stdout, "Last accessed date   : %u-%u-%u\n", adate_y, adate_m, adate_d);

  ret = fat_is_fat32_fs(sb, &is_fat32_fs);
  if (ret != 0) {
    return;
  }

  if (!is_fat32_fs) {
    str = NULL;
    fprintf(stdout, "Access rights bitmap : ");
    if (dentry->starthi & ARB_OWN_DRC_REQ_PERM) {
      str = "owner delete/rename/attribute change requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_OWN_EXE_REQ_PERM) {
      str = "owner execute requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_OWN_WM_REQ_PERM) {
      str = "owner write/modify requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_OWN_RC_REQ_PERM) {
      str = "owner read/copy requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_GRP_DRC_REQ_PERM) {
      str = "group delete/rename/attribute change requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_GRP_EXE_REQ_PERM) {
      str = "group execute requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_GRP_WM_REQ_PERM) {
      str = "group write/modify requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_GRP_RC_REQ_PERM) {
      str = "group read/copy requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_WORLD_DRC_REQ_PERM) {
      str = "world delete/rename/attribute change requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_WORLD_EXE_REQ_PERM) {
      str = "world execute requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_WORLD_WM_REQ_PERM) {
      str = "world write/modify requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi & ARB_WORLD_RC_REQ_PERM) {
      str = "world read/copy requires permission";
      fprintf(stdout, "%s, ", str);
    } 
    if (dentry->starthi == ARB_NONE) {
      str = FAT_DUMMY_STR;
      fprintf(stdout, "%s", str);
    }
    fprintf(stdout, "\n");
  }

  mtime_h = (dentry->time >> 11) & 0x001F;
  mtime_m = (dentry->time >> 5) & 0x003F;
  mtime_s = (dentry->time & 0x001F) << 1;
  fprintf(stdout, "Last modified time   : %u:%u:%u\n", mtime_h, mtime_m, mtime_s);

  mdate_y = ((dentry->date >> 9) & 0x007F) + 1980;
  mdate_m = (dentry->date >> 5) & 0x000F;
  mdate_d = dentry->date & 0x001F;
  fprintf(stdout, "Last modified date   : %u-%u-%u\n", mdate_y, mdate_m, mdate_d);

  fprintf(stdout, "First cluster        : ");
  if (is_fat32_fs) {
    fprintf(stdout, "%u\n", ((uint32_t)dentry->starthi << 16) | ((uint32_t)dentry->start));
  } else {
    fprintf(stdout, "%u\n", dentry->start);
  }

  fprintf(stdout, "Size                 : %u\n", dentry->size);
}
