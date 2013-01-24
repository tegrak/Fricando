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
static int32_t openfs_ext4(int32_t argc, char **argv);
static int32_t closefs_ext4(int32_t argc, char **argv);
static int32_t pwddir_ext4(int32_t argc, char **argv);
static int32_t cddir_ext4(int32_t argc, char **argv);
static int32_t lsdir_ext4(int32_t argc, char **argv);
static int32_t mkdir_ext4(int32_t argc, char **argv);
static int32_t rm_ext4(int32_t argc, char **argv);
static int32_t mkfile_ext4(int32_t argc, char **argv);
static int32_t readfile_ext4(int32_t argc, char **argv);
static int32_t writefile_ext4(int32_t argc, char **argv);

/*
 * Global Variable Definition
 */
/*
 * Ext4 filesystem operation table
 */
fs_opt_t fs_opt_tbl_ext4[FS_OPT_TBL_NUM_MAX] = {
  [0] = {
    .opt_hdl = openfs_ext4,
    .opt_cmd = FS_OPT_CMD_DEFAULT_OPENFS,
  },

  [1] = {
    .opt_hdl = closefs_ext4,
    .opt_cmd = FS_OPT_CMD_DEFAULT_CLOSEFS,
  },

  [2] = {
    .opt_hdl = pwddir_ext4,
    .opt_cmd = "pwd",
  },

  [3] = {
    .opt_hdl = cddir_ext4,
    .opt_cmd = "cd",
  },

  [4] = {
    .opt_hdl = lsdir_ext4,
    .opt_cmd = "ls",
  },

  [5] = {
    .opt_hdl = mkdir_ext4,
    .opt_cmd = "mkdir",
  },

  [6] = {
    .opt_hdl = rm_ext4,
    .opt_cmd = "rm",
  },

  [7] = {
    .opt_hdl = mkfile_ext4,
    .opt_cmd = "mkfile",
  },

  [8] = {
    .opt_hdl = readfile_ext4,
    .opt_cmd = "rdfile",
  },

  [9] = {
    .opt_hdl = writefile_ext4,
    .opt_cmd = "wtfile",
  },
};

/*
 * Function Definition
 */
static int32_t openfs_ext4(int32_t argc, char **argv)
{
  fprintf(stdout, "info: open Ext4 filesystem successfully.\n");

  return 0;
}

static int32_t closefs_ext4(int32_t argc, char **argv)
{
  return -1;
}

static int32_t pwddir_ext4(int32_t argc, char **argv)
{
  return -1;
}

static int32_t cddir_ext4(int32_t argc, char **argv)
{
  return -1;
}

static int32_t lsdir_ext4(int32_t argc, char **argv)
{
  return -1;
}

static int32_t mkdir_ext4(int32_t argc, char **argv)
{
  return -1;
}

static int32_t rm_ext4(int32_t argc, char **argv)
{
  return -1;
}

static int32_t mkfile_ext4(int32_t argc, char **argv)
{
  return -1;
}

static int32_t readfile_ext4(int32_t argc, char **argv)
{
  return -1;
}

static int32_t writefile_ext4(int32_t argc, char **argv)
{
  return -1;
}
