/**
 * libext4.h - The header of libext4.
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
 * along with this program (in the main directory of the NTFS-3G
 * distribution in the file COPYING); if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifndef _LIBEXT4_H
#define _LIBEXT4_H

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef HAVE_STDINT_H
#include <stdint.h>
#endif

#ifdef DEBUG
// Add code here
#endif

/*
 * Macro Definition
 */
/*
 * Ext4 inode mode for file mode
 */
#define EXT4_INODE_MODE_S_IXOTH   (0x1)
#define EXT4_INODE_MODE_S_IWOTH   (0x2)
#define EXT4_INODE_MODE_S_IROTH   (0x4)
#define EXT4_INODE_MODE_S_IXGRP   (0x8)
#define EXT4_INODE_MODE_S_IWGRP   (0x10)
#define EXT4_INODE_MODE_S_IRGRP   (0x20)
#define EXT4_INODE_MODE_S_IXUSR   (0x40)
#define EXT4_INODE_MODE_S_IWUSR   (0x80)
#define EXT4_INODE_MODE_S_IRUSR   (0x100)
#define EXT4_INODE_MODE_S_ISVTX   (0x200)
#define EXT4_INODE_MODE_S_ISGID   (0x400)
#define EXT4_INODE_MODE_S_ISUID   (0x800)

/*
 * Ext4 inode mode for file type
 */
#define EXT4_INODE_MODE_S_IFIFO   (0x1000)
#define EXT4_INODE_MODE_S_IFCHR   (0x2000)
#define EXT4_INODE_MODE_S_IFDIR   (0x4000)
#define EXT4_INODE_MODE_S_IFBLK   (0x6000)
#define EXT4_INODE_MODE_S_IFREG   (0x8000)
#define EXT4_INODE_MODE_S_IFLNK   (0xA000)
#define EXT4_INODE_MODE_S_IFSOCK  (0xC000)

/*
 * Type Definition
 */
struct ext4_group_desc_min
{
 __le32 bg_block_bitmap_lo;
 __le32 bg_inode_bitmap_lo;
 __le32 bg_inode_table_lo;
 __le16 bg_free_blocks_count_lo;
 __le16 bg_free_inodes_count_lo;
 __le16 bg_used_dirs_count_lo;
 __le16 bg_flags;
 __u32 bg_reserved[3];
};

/*
 * Function Declaration
 */
int32_t ext4_fill_sb(struct ext4_super_block *sb);
int32_t ext4_fill_blk_sz(const struct ext4_super_block *sb, int32_t *blk_sz);
int32_t ext4_fill_bg_groups(const struct ext4_super_block *sb, int32_t *bg_groups);
int32_t ext4_fill_bg_desc(const struct ext4_super_block *sb, int32_t bg_groups, struct ext4_group_desc_min *bg_desc);
int32_t ext4_fill_inode(const struct ext4_super_block *sb, const struct ext4_group_desc_min *bg_desc, uint32_t inode_num, struct ext4_inode *inode);
 
void ext4_show_stats(const struct ext4_super_block *sb, int32_t bg_groups, const struct ext4_group_desc_min *bg_desc);
void ext4_show_inode_stat(const struct ext4_super_block *sb, uint32_t inode_num, const struct ext4_inode *inode);

#endif /* _LIBEXT4_H */
