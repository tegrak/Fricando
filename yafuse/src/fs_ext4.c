/**
 * fs_ext4.c - The entry of Ext4 filesystem.
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

#include "filesystem.h"
#include "fs_ext4.h"

/*
 * Macro Definition
 */

/*
 * Type Definition
 */
typedef struct {
  int32_t mounted;
  struct ext4_super_block *sb;
  int32_t bg_groups;
  struct ext4_group_desc_min *bg_desc;
} fs_info_ext4_t;

/*
 * Function Declaration
 */
static int32_t fs_do_mount(int32_t argc, char **argv);
static int32_t fs_do_umount(int32_t argc, char **argv);
static int32_t fs_do_stats(int32_t argc, char **argv);
static int32_t fs_do_stat(int32_t argc, char **argv);
static int32_t fs_do_pwd(int32_t argc, char **argv);
static int32_t fs_do_cd(int32_t argc, char **argv);
static int32_t fs_do_ls(int32_t argc, char **argv);
static int32_t fs_do_mkdir(int32_t argc, char **argv);
static int32_t fs_do_rm(int32_t argc, char **argv);
static int32_t fs_do_read(int32_t argc, char **argv);
static int32_t fs_do_write(int32_t argc, char **argv);

/*
 * Global Variable Definition
 */
/*
 * Ext4 filesystem operation table
 */
fs_opt_t fs_opt_tbl_ext4[FS_OPT_TBL_NUM_MAX] = {
  [0] = {
    .opt_hdl = fs_do_mount,
    .opt_cmd = FS_OPT_CMD_MOUNT,
  },

  [1] = {
    .opt_hdl = fs_do_umount,
    .opt_cmd = FS_OPT_CMD_UMOUNT,
  },

  [2] = {
    .opt_hdl = fs_do_stats,
    .opt_cmd = "stats",
  },

  [3] = {
    .opt_hdl = fs_do_stat,
    .opt_cmd = "stat",
  },

  [4] = {
    .opt_hdl = fs_do_pwd,
    .opt_cmd = "pwd",
  },

  [5] = {
    .opt_hdl = fs_do_cd,
    .opt_cmd = "cd",
  },

  [6] = {
    .opt_hdl = fs_do_ls,
    .opt_cmd = "ls",
  },

  [7] = {
    .opt_hdl = fs_do_mkdir,
    .opt_cmd = "mkdir",
  },

  [8] = {
    .opt_hdl = fs_do_rm,
    .opt_cmd = "rm",
  },

  [9] = {
    .opt_hdl = fs_do_read,
    .opt_cmd = "read",
  },

  [10] = {
    .opt_hdl = fs_do_write,
    .opt_cmd = "write",
  },

  [11] = {
    .opt_hdl = NULL,
    .opt_cmd = NULL,
  }
};

static fs_info_ext4_t fs_info;

/*
 * Function Definition
 */
static int32_t fs_do_mount(int32_t argc, char **argv)
{
  const char *name = NULL;
  struct ext4_super_block *sb = NULL;
  int32_t bg_groups = 0;
  struct ext4_group_desc_min *bg_desc = NULL;
  int32_t ret = -1;

  if (argc < 2 || argv == NULL) {
    error("invalid args!");
    return -1;
  }

  name = (const char *)argv[1];
  if (name == NULL) {
    error("invalid args!");
    return -1;
  }

  if (fs_info.mounted) {
    info("umount ext4 filesystem first.");
    return 0;
  }

  /*
   * Open Ext4 image
   */
  ret = io_open(name);
  if (ret != 0) {
    error("failed to open io!");
    return -1;
  }

  /*
   * Fill in Ext4 superblock
   */
  sb = (struct ext4_super_block *)malloc(sizeof(struct ext4_super_block));
  if (sb == NULL) {
    error("failed to malloc sb!");
    ret = -1;
    goto fs_do_mount_fail;
  }
  memset((void *)sb, 0, sizeof(struct ext4_super_block));

  ret = ext4_fill_sb(sb);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  /*
   * Fill in Ext4 block group number
   */
  ret = ext4_fill_bg_groups((const struct ext4_super_block *)sb, &bg_groups);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  /*
   * Fill in Ext4 block group descriptor
   */
  bg_desc = (struct ext4_group_desc_min *)malloc(sb->s_desc_size * bg_groups);
  if (bg_desc == NULL) {
    error("failed to malloc bg desc!");
    ret = -1;
    goto fs_do_mount_fail;
  }
  memset((void *)bg_desc, 0, sb->s_desc_size * bg_groups);

  ret = ext4_fill_bg_desc((const struct ext4_super_block *)sb, bg_groups, bg_desc);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  /*
   * Init Ext4 filesytem info
   */
  fs_info.mounted = 1;
  fs_info.sb = sb;
  fs_info.bg_groups = bg_groups;
  fs_info.bg_desc = bg_desc;

  info("mount ext4 filesystem successfully.");

  return 0;

 fs_do_mount_fail:

  info("failed to mount ext4 filesystem.");

  if (bg_desc != NULL) free(bg_desc);
  if (sb != NULL) free(sb);

  io_close();

  memset((void *)&fs_info, 0, sizeof(fs_info_ext4_t));

  return ret;
}

static int32_t fs_do_umount(int32_t argc, char **argv)
{
  if (fs_info.mounted) {
    info("umount ext4 filesystem successfully.");
  }

  if (fs_info.bg_desc != NULL) free(fs_info.bg_desc);
  if (fs_info.sb != NULL) free(fs_info.sb);

  io_close();

  memset((void *)&fs_info, 0, sizeof(fs_info_ext4_t));

  return 0;
}

static int32_t fs_do_stats(int32_t argc, char **argv)
{
  if (fs_info.sb == NULL
      || fs_info.bg_groups <= 0
      || fs_info.bg_desc == NULL) {
    error("failed to stats ext4 filesystem!");
    return -1;
  }

  ext4_show_stats((const struct ext4_super_block *)fs_info.sb, fs_info.bg_groups, (const struct ext4_group_desc_min *)fs_info.bg_desc);

  return 0;
}

static int32_t fs_do_stat(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_pwd(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_cd(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_ls(int32_t argc, char **argv)
{
  const char *name = NULL;

  if (argc > 2 || argv == NULL) {
    error("invalid args!");
    return -1;
  }

  if (argc == 2) {
    name = (const char *)argv[1];
    if (name == NULL) {
      error("invalid args!");
      return -1;
    }
  }

  return 0;
}

static int32_t fs_do_mkdir(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_rm(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_read(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_write(int32_t argc, char **argv)
{
  return -1;
}
