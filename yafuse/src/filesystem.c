/**
 * filesystem.c - The entry of filesystem.
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
#ifdef HAVE_STRING_H
#include <string.h>
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

#include "include/debug.h"

#include "filesystem.h"

/*
 * Macro Definition
 */

/*
 * Type Definition
 */

/*
 * Global Variable Definition
 */
static fs_opt_t* fs_opt_tbl_list[FS_TYPE_NUM_MAX];
static int32_t fs_opt_tbl_list_len = 0;

/*
 * Function Declaration
 */

/*
 * Function Definition
 */
/*
 * Register filesystem operation table
 */
int32_t fs_register(fs_opt_t *fs_opt_tbl)
{
  if (fs_opt_tbl == NULL) {
    error("invalid args!");
    return -1;
  }

  ++fs_opt_tbl_list_len;
  if (fs_opt_tbl_list_len > FS_TYPE_NUM_MAX) {
    error("filesystem type overflow!");
    return -1;
  }

  fs_opt_tbl_list[fs_opt_tbl_list_len - 1] = fs_opt_tbl;

  return 0;
}

/*
 * Unregister filesystem
 */
void fs_unregister()
{
}

/*
 * Open filesystem
 */
int32_t fs_open(const char *fs_name)
{
  int32_t argc = 0;
  char* argv[FS_OPT_CMD_ARG_NUM_MAX] = {NULL};
  fs_opt_handle_t handle = NULL;
  int32_t i = 0;
  int32_t opt_tbl_list_idx = -1;
  int32_t ret = 0;

  argc = 2;
  argv[0] = FS_OPT_CMD_MOUNT;
  argv[1] = (char *)fs_name;

  for (i = 0; i < fs_opt_tbl_list_len; ++i) {
    handle = fs_opt_hdl_match(i, FS_OPT_CMD_MOUNT);
    if (handle != NULL) {
      ret = handle(argc, argv);
      if (ret == 0) {
        opt_tbl_list_idx = i;
        break;
      }
    }
  }

  return opt_tbl_list_idx;
}

/*
 * Close filesystem
 */
void fs_close(int32_t fs_type)
{
  int32_t argc = 0;
  char* argv[FS_OPT_CMD_ARG_NUM_MAX] = {NULL};
  fs_opt_handle_t handle = NULL;

  if (fs_type < 0 || fs_type >= fs_opt_tbl_list_len) {
    return;
  }

  argc = 2;
  argv[0] = FS_OPT_CMD_UMOUNT;
  argv[1] = (char *)NULL;

  handle = fs_opt_hdl_match(fs_type, FS_OPT_CMD_UMOUNT);
  if (handle != NULL) {
    (void)handle(argc, argv);
  }
}

/*
 * Match opt handle with opt command
 */
fs_opt_handle_t fs_opt_hdl_match(int32_t fs_type, const char *fs_cmd)
{
  int32_t i = 0;
  int32_t len_opt_cmd = 0, len_fs_cmd = 0;
  fs_opt_handle_t handle = NULL;

  if (fs_type < 0
      || fs_type >= fs_opt_tbl_list_len
      || fs_cmd == NULL) {
    return ((fs_opt_handle_t)NULL);
  }

  len_fs_cmd = strlen(fs_cmd);

  for (i = 0; i < FS_OPT_TBL_NUM_MAX; ++i) {
    if (fs_opt_tbl_list[fs_type][i].opt_cmd == NULL) {
      break;
    }
     
    len_opt_cmd = strlen((char *)(fs_opt_tbl_list[fs_type][i].opt_cmd));

    if (len_opt_cmd > 0 && len_opt_cmd <= len_fs_cmd) {
      if (strncmp((char *)(fs_opt_tbl_list[fs_type][i].opt_cmd), (char *)fs_cmd, len_opt_cmd) == 0) {
        handle = fs_opt_tbl_list[fs_type][i].opt_hdl;
        break;
      }
    }
  }

  return handle;
}

/*
 * Get number of filesystem opt
 */
int32_t fs_opt_num(int32_t fs_type)
{
  int32_t i = 0;

  if (fs_type < 0 || fs_type >= fs_opt_tbl_list_len) {
    return 0;
  }

  for (i = 0; i < FS_OPT_TBL_NUM_MAX; ++i) {
    if (fs_opt_tbl_list[fs_type][i].opt_cmd == NULL) {
      break;
    }
  }

  return i;
}

/*
 * Enumerate filesystem opt commond
 */
const char* fs_opt_cmd_enum(int32_t fs_type, int32_t opt_idx)
{
  if (fs_type < 0
      || fs_type >= fs_opt_tbl_list_len
      || opt_idx < 0
      || opt_idx >= FS_OPT_TBL_NUM_MAX) {
    return ((const char *)NULL);
  }

  return fs_opt_tbl_list[fs_type][opt_idx].opt_cmd;
}
