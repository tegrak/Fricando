/**
 * fs_fat32.c - The entry of FAT32 filesystem.
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

#ifdef DEBUG
// Add code here
#endif

#include "filesystem.h"

/*
 * Macro Definition
 */

/*
 * Type Definition
 */

/*
 * Function Declaration
 */
static int32_t fs_do_openfs(int32_t argc, char **argv);
static int32_t fs_do_closefs(int32_t argc, char **argv);
static int32_t fs_do_pwd(int32_t argc, char **argv);
static int32_t fs_do_cd(int32_t argc, char **argv);
static int32_t fs_do_ls(int32_t argc, char **argv);
static int32_t fs_do_mkdir(int32_t argc, char **argv);
static int32_t fs_do_rm(int32_t argc, char **argv);
static int32_t fs_do_mkfile(int32_t argc, char **argv);
static int32_t fs_do_readfile(int32_t argc, char **argv);
static int32_t fs_do_writefile(int32_t argc, char **argv);

/*
 * Global Variable Definition
 */
/*
 * FAT32 filesystem operation table
 */
fs_opt_t fs_opt_tbl_fat32[FS_OPT_TBL_NUM_MAX] = {
  [0] = {
    .opt_hdl = fs_do_openfs,
    .opt_cmd = FS_OPT_CMD_DEFAULT_OPENFS,
  },

  [1] = {
    .opt_hdl = fs_do_closefs,
    .opt_cmd = FS_OPT_CMD_DEFAULT_CLOSEFS,
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
    .opt_hdl = fs_do_mkfile,
    .opt_cmd = "mkfile",
  },

  [8] = {
    .opt_hdl = fs_do_readfile,
    .opt_cmd = "rdfile",
  },

  [9] = {
    .opt_hdl = fs_do_writefile,
    .opt_cmd = "wtfile",
  },

  [10] = {
    .opt_hdl = NULL,
    .opt_cmd = NULL,
  }
};

/*
 * Function Definition
 */
static int32_t fs_do_openfs(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_closefs(int32_t argc, char **argv)
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

static int32_t fs_do_mkfile(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_readfile(int32_t argc, char **argv)
{
  return -1;
}

static int32_t fs_do_writefile(int32_t argc, char **argv)
{
  return -1;
}
