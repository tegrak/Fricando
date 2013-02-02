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
#include "include/libext4/types.h"
#include "include/libext4/ext4.h"
#include "include/libext4/ext4_extents.h"
#include "include/libext4/ext4_jbd2.h"
#include "include/libext4/jbd2.h"
#include "include/libext4/libext4.h"

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
} fs_info_ext4_t;

/*
 * Function Declaration
 */
static int32_t fs_do_mount(int32_t argc, char **argv);
static int32_t fs_do_umount(int32_t argc, char **argv);
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
    .opt_hdl = fs_do_pwd,
    .opt_cmd = "pwd",
  },

  [3] = {
    .opt_hdl = fs_do_cd,
    .opt_cmd = "cd",
  },

  [4] = {
    .opt_hdl = fs_do_ls,
    .opt_cmd = "ls",
  },

  [5] = {
    .opt_hdl = fs_do_mkdir,
    .opt_cmd = "mkdir",
  },

  [6] = {
    .opt_hdl = fs_do_rm,
    .opt_cmd = "rm",
  },

  [7] = {
    .opt_hdl = fs_do_read,
    .opt_cmd = "read",
  },

  [8] = {
    .opt_hdl = fs_do_write,
    .opt_cmd = "write",
  },

  [9] = {
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
    info("umount ext4 filesystem first!");
    return 0;
  }

  sb = (struct ext4_super_block *)malloc(sizeof(struct ext4_super_block));
  if (sb == NULL) {
    error("failed to malloc!");
    return -1;
  }

  ret = ext4_fill_super(name, sb);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  fs_info.mounted = 1;
  fs_info.sb = sb;

  info("mount ext4 filesystem successfully.");

  return 0;

 fs_do_mount_fail:
  info("failed to mount ext4 filesystem!");
  if (sb != NULL) free(sb);
  return ret;
}

static int32_t fs_do_umount(int32_t argc, char **argv)
{
  if (fs_info.mounted) {
    info("umount ext4 filesystem successfully.");
  }

  if (fs_info.sb != NULL) free(fs_info.sb);

  memset((void *)&fs_info, 0, sizeof(fs_info_ext4_t));

  return 0;
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
  return -1;
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
