/**
 * libfat.h - The header of libfat.
 *
 * Copyright (c) 2013-2014 angersax@gmail.com
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program (in the main directory of the distribution
 * in the file COPYING); if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifndef _LIBFAT_H
#define _LIBFAT_H

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef HAVE_STDINT_H
#include <stdint.h>
#endif

#ifdef DEBUG
// Add code here
#endif

#include "include/libfat/msdos_fs.h"

/*
 * Macro Definition
 */
#define SECTOR_SIZE_MAX  (4096)

/*
 * Dentry name
 */
#define MSDOS_NAME_BASE_LEN  (8)
#define MSDOS_NAME_EXT_LEN   (MSDOS_NAME - MSDOS_NAME_BASE_LEN)

/*
 * Dentry lcase
 */
#define LCASE_NONE                       0x00
#define LCASE_READ_REQ_PASS              0x01
#define LCASE_WRITE_REQ_PASS             0x02
#define LCASE_DEL_REQ_PASS               0x04
#define LCASE_RESERVED                   0x08
#define LCASE_DISABLE_CHKSUM             0x10
#define LCASE_IGNORE_CLOSE_CHKSUM_ERR    0x20
#define LCASE_PARTIAL_CLOSE_DEFAULT      0x40
#define LCASE_MODIFY_DEFAULT_OPEN_RULES  0x80

/*
 * Dentry access rights bitmap
 */
#define ARB_NONE                0x0000
#define ARB_OWN_DRC_REQ_PERM    0x0001
#define ARB_OWN_EXE_REQ_PERM    0x0002
#define ARB_OWN_WM_REQ_PERM     0x0004
#define ARB_OWN_RC_REQ_PERM     0x0008
#define ARB_GRP_DRC_REQ_PERM    0x0010
#define ARB_GRP_EXE_REQ_PERM    0x0020
#define ARB_GRP_WM_REQ_PERM     0x0040
#define ARB_GRP_RC_REQ_PERM     0x0080
#define ARB_WORLD_DRC_REQ_PERM  0x0100
#define ARB_WORLD_EXE_REQ_PERM  0x0200
#define ARB_WORLD_WM_REQ_PERM   0x0400
#define ARB_WORLD_RC_REQ_PERM   0x0800

/*
 * Type Definition
 */
struct fat_super_block {
  struct fat_boot_sector bs;
  struct fat_boot_bsx bb;

  /*
   * The following fields are only used by FAT32
   */
  struct fat_boot_fsinfo bf;
};

/*
 * Function Declaration
 */
int32_t fat_fill_sb(struct fat_super_block *sb);
int32_t fat_is_fat32_fs(const struct fat_super_block *sb, int32_t *status);
int32_t fat_fill_clus2sec(const struct fat_super_block *sb, int32_t cluster, int32_t *sector);
int32_t fat_fill_dent_start(const struct fat_super_block *sb, const struct msdos_dir_entry *dentry, int32_t *start_cluster);
int32_t fat_fill_root_dentries(const struct fat_super_block *sb, int32_t *dentries);
int32_t fat_fill_root_dentry(const struct fat_super_block *sb, int32_t dentries, struct msdos_dir_slot *dslot, struct msdos_dir_entry *dentry);
int32_t fat_fill_dentries(const struct fat_super_block *sb, int32_t cluster, int32_t *dentries);
int32_t fat_fill_dentry(const struct fat_super_block *sb, int32_t cluster, int32_t dentries, struct msdos_dir_slot *dslot, struct msdos_dir_entry *dentry);
int32_t fat_dent_attr_is_dir(const struct msdos_dir_entry *dentry, int32_t *status);

void fat_show_stats(const struct fat_super_block *sb);
void fat_show_dslot(const struct fat_super_block *sb, const struct msdos_dir_slot *dslot);
void fat_show_dentry(const struct fat_super_block *sb, const struct msdos_dir_entry *dentry);

#endif /* _LIBFAT_H */
