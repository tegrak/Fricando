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
 * along with this program (in the main directory of the distribution
 * in the file COPYING); if not, write to the Free Software
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
#define FS_EXT4_PATH_LEN_MAX  (255)

#define FS_EXT4_STAT_INO_DELIM_L  '<'
#define FS_EXT4_STAT_INO_DELIM_R  '>'

/*
 * Type Definition
 */
typedef struct {
  int32_t ino;
  const char *root;
  char path[FS_EXT4_PATH_LEN_MAX + 1];
  int32_t dentries;
  struct ext4_dir_entry_2 *dentry;
} fs_ext4_cwd_t;

typedef struct {
  /*
   * General info
   */
  fs_ext4_cwd_t cwd;

  /*
   * Filesystem info
   */
  struct ext4_super_block *sb;
  int32_t bg_groups;
  struct ext4_group_desc_min *bg_desc;
} fs_ext4_info_t;

/*
 * Function Declaration
 */
static int32_t fs_parse_ino(const char *name, int32_t *ino);
static int32_t fs_name2ino(const char *name, int32_t dentries, const struct ext4_dir_entry_2 *dentry, int32_t *ino);
static int32_t fs_ino2dentry(int32_t ino, const struct ext4_super_block *sb, const struct ext4_group_desc_min *bg_desc, int32_t *dentries, struct ext4_dir_entry_2 **dentry);
static int32_t fs_path_push(const char *dirname, char *path);
static int32_t fs_path_pop(char *path);

static int32_t fs_do_mount(int32_t argc, const char **argv);
static int32_t fs_do_umount(int32_t argc, const char **argv);
static int32_t fs_do_stats(int32_t argc, const char **argv);
static int32_t fs_do_stat(int32_t argc, const char **argv);
static int32_t fs_do_pwd(int32_t argc, const char **argv);
static int32_t fs_do_cd(int32_t argc, const char **argv);
static int32_t fs_do_ls(int32_t argc, const char **argv);
static int32_t fs_do_mkdir(int32_t argc, const char **argv);
static int32_t fs_do_rm(int32_t argc, const char **argv);
static int32_t fs_do_read(int32_t argc, const char **argv);
static int32_t fs_do_write(int32_t argc, const char **argv);

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

static fs_ext4_info_t ext4_info;

/*
 * Function Definition
 */
static int32_t fs_parse_ino(const char *name, int32_t *ino)
{
  char *buf = NULL;
  size_t len_name = 0, len_buf = 0;
  int32_t val = 0;
  int32_t ret = 0;

  if (name == NULL || ino == NULL) {
    return -1;
  }

  /*
   * len_name <= len(FS_EXT4_STAT_INO_DELIM_L) + len(FS_EXT4_STAT_INO_DELIM_R)
   */
  len_name = strlen(name);
  if (len_name <= 2) {
    return -1;
  }

  if (name[0] != FS_EXT4_STAT_INO_DELIM_L && name[len_name - 1] != FS_EXT4_STAT_INO_DELIM_R) {
    return -1;
  }

  /*
   * len_buf = len_name - (len(FS_EXT4_STAT_INO_DELIM_L) + len(FS_EXT4_STAT_INO_DELIM_R)) + 1;
   */
  len_buf = len_name - (1 + 1) + 1;

  buf = (char *)malloc(len_buf);
  if (buf == NULL) {
    return -1;
  }
  memset((void *)buf, 0, len_buf);
  strncpy((void *)buf, (const void *)&name[1], len_buf - 1);

  val = atoi((const char *)buf);
  if (val < EXT4_ROOT_INO) {
    ret = -1;
    goto fs_parse_ino_done;
  }

  *ino = val;

  ret = 0;

 fs_parse_ino_done:

  if (buf != NULL) {
    free(buf);
    buf = NULL;
  }

  return ret;
}

static int32_t fs_name2ino(const char *name, int32_t dentries, const struct ext4_dir_entry_2 *dentry, int32_t *ino)
{
  size_t len_s1 = 0, len_s2 = 0;
  int32_t i = 0;

  if (name == NULL || dentries == 0 || dentry == NULL || ino == NULL ) {
    return -1;
  }

  for (i = 0; i < dentries; ++i) {
    len_s1 = dentry[i].name_len;
    len_s2 = strlen(name);

    if (len_s1 == len_s2) {
      if (0 == strncmp(dentry[i].name, name, len_s1)) {
        *ino = (int32_t)dentry[i].inode;
        break;
      }
    }
  }

  return 0;
}

static int32_t fs_ino2dentry(int32_t ino, const struct ext4_super_block *sb, const struct ext4_group_desc_min *bg_desc, int32_t *dentries, struct ext4_dir_entry_2 **dentry)
{
  struct ext4_inode inode;
  int32_t extents = 0;
  struct ext4_extent *extent = NULL;
  int32_t dentries_new = 0;
  int32_t status = 0;
  int32_t ret = 0;

  if (ino == EXT4_UNUSED_INO
      || ino == EXT4_BAD_INO
      || sb == NULL
      || bg_desc == NULL
      || dentries == NULL
      || dentry == NULL) {
    return -1;
  }

  /*
   * Fill in Ext4 inode
   */
  memset((void *)&inode, 0, sizeof(struct ext4_inode));

  ret = ext4_fill_inode((const struct ext4_super_block *)sb,
                        (const struct ext4_group_desc_min *)bg_desc,
                        ino,
                        &inode);
  if (ret != 0) {
    return -1;
  }

  ret = ext4_inode_mode_is_dir((const struct ext4_inode *)&inode, &status);
  if (ret != 0 || status == 0) {
    return -1;
  }

  /*
   * Fill in Ext4 entents
   */
  ret = ext4_fill_extents((const struct ext4_inode *)&inode, &extents);
  if (ret != 0) {
    return -1;
  }

  /*
   * Fill in Ext4 entent list
   * Attention: 'extents = 1' required
   */
  extent = (struct ext4_extent *)malloc(sizeof(struct ext4_extent) * extents);
  if (extent == NULL) {
    return -1;    
  }
  memset((void *)extent, 0, sizeof(struct ext4_extent) * extents);

  ret = ext4_fill_extent((const struct ext4_inode *)&inode, extents, extent);
  if (ret != 0) {
    goto fs_ino2dentry_done;
  }

  /*
   * Fill in Ext4 dentries
   */
  ret = ext4_fill_dentries((const struct ext4_super_block *)sb,
                           (const struct ext4_extent *)&extent[0],
                           &dentries_new);
  if (ret != 0) {
    goto fs_ino2dentry_done;
  }

  /*
   * Fill in Ext4 dentry list
   */
  if (dentries_new > *dentries) {
    *dentry = (struct ext4_dir_entry_2 *)realloc((void *)*dentry, sizeof(struct ext4_dir_entry_2) * dentries_new);
    if (*dentry == NULL) {
      goto fs_ino2dentry_done;
    }
    memset((void *)*dentry, 0, sizeof(struct ext4_dir_entry_2) * dentries_new);
  }

  *dentries = dentries_new;

  ret = ext4_fill_dentry((const struct ext4_super_block *)sb,
                         (const struct ext4_extent *)&extent[0],
                         *dentries,
                         *dentry);
  if (ret != 0) {
    goto fs_ino2dentry_done;
  }

 fs_ino2dentry_done:

  if (extent != NULL) {
    free(extent);
    extent = NULL;
  }

  return ret;
}

static int32_t fs_path_push(const char *dirname, char *path)
{
  size_t len_path = 0, len_name;
  char *ptr = NULL;

  if (dirname == NULL || path == NULL) {
    return -1;
  }

  len_path = strlen(path);
  len_name = strlen(dirname);

  if ((FS_EXT4_PATH_LEN_MAX + 1 - len_path) < (strlen(FS_PATH_DELIM) + len_name + 1)) {
    return -1;
  }

  ptr = path + len_path;

  memcpy((void *)ptr, (const void *)FS_PATH_DELIM, strlen(FS_PATH_DELIM));
  memcpy((void *)(ptr + strlen(FS_PATH_DELIM)), (const void *)dirname, len_name);

  return 0;
}

static int32_t fs_path_pop(char *path)
{
  const char *str = NULL;
  char *ptr = NULL;
  size_t len = 0;

  if (path == NULL) {
    return -1;
  }

  str = FS_PATH_DELIM;

  ptr = strrchr((const char *)path, str[0]);
  if (ptr != NULL) {
    len = strlen(ptr);
    memset((void *)ptr, 0, len);
  }

  return 0;
}

static int32_t fs_do_mount(int32_t argc, const char **argv)
{
  const char *name = NULL;
  struct ext4_super_block *sb = NULL;
  int32_t bg_groups = 0;
  struct ext4_group_desc_min *bg_desc = NULL;
  int32_t ret = -1;

  if (argc < 2 || argv == NULL) {
    error("invalid ext4 args!");
    return -1;
  }

  name = argv[1];
  if (name == NULL) {
    error("invalid ext4 args!");
    return -1;
  }

  /*
   * Open Ext4 image
   */
  ret = io_open(name);
  if (ret != 0) {
    error("failed to open ext4 io!");
    return -1;
  }

  /*
   * Fill in Ext4 superblock
   */
  sb = (struct ext4_super_block *)malloc(sizeof(struct ext4_super_block));
  if (sb == NULL) {
    error("failed to malloc ext4 sb!");
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
  if (sb->s_feature_incompat & EXT4_FEATURE_INCOMPAT_64BIT
      && sb->s_desc_size > EXT4_MIN_DESC_SIZE) {
    error("not support ext4 size of 2^64 blocks!");
    ret = -1;
    goto fs_do_mount_fail;
  }

  bg_desc = (struct ext4_group_desc_min *)malloc(sb->s_desc_size * bg_groups);
  if (bg_desc == NULL) {
    error("failed to malloc ext4 bg desc!");
    ret = -1;
    goto fs_do_mount_fail;
  }
  memset((void *)bg_desc, 0, sb->s_desc_size * bg_groups);

  ret = ext4_fill_bg_desc((const struct ext4_super_block *)sb, bg_groups, bg_desc);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  /*
   * Init Ext4 info
   */
  ext4_info.cwd.ino = EXT4_ROOT_INO;
  ext4_info.cwd.root = FS_ROOT_PATH;
  memset((void *)ext4_info.cwd.path, 0, FS_EXT4_PATH_LEN_MAX + 1);
  ext4_info.cwd.dentries = 0;
  ext4_info.cwd.dentry = NULL;
  ext4_info.sb = sb;
  ext4_info.bg_groups = bg_groups;
  ext4_info.bg_desc = bg_desc;

  /*
   * Fill in Ext4 dentry list
   */
  ret = fs_ino2dentry(ext4_info.cwd.ino,
                      (const struct ext4_super_block *)ext4_info.sb,
                      (const struct ext4_group_desc_min *)ext4_info.bg_desc,
                      &ext4_info.cwd.dentries,
                      &ext4_info.cwd.dentry);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  return 0;

 fs_do_mount_fail:

  if (ext4_info.cwd.dentry != NULL) {
    free(ext4_info.cwd.dentry);
    ext4_info.cwd.dentry = NULL;
  }

  if (bg_desc != NULL) {
    free(bg_desc);
    bg_desc = NULL;
  }

  if (sb != NULL) {
    free(sb);
    sb = NULL;
  }

  io_close();

  memset((void *)&ext4_info, 0, sizeof(fs_ext4_info_t));

  return ret;
}

static int32_t fs_do_umount(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  if (ext4_info.cwd.dentry != NULL) {
    free(ext4_info.cwd.dentry);
    ext4_info.cwd.dentry = NULL;
  }

  if (ext4_info.bg_desc != NULL) {
    free(ext4_info.bg_desc);
    ext4_info.bg_desc = NULL;
  }

  if (ext4_info.sb != NULL) {
    free(ext4_info.sb);
    ext4_info.sb = NULL;
  }

  io_close();

  memset((void *)&ext4_info, 0, sizeof(fs_ext4_info_t));

  return 0;
}

static int32_t fs_do_stats(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  if (ext4_info.sb == NULL
      || ext4_info.bg_groups <= 0
      || ext4_info.bg_desc == NULL) {
    error("failed to stats ext4 filesystem!");
    return -1;
  }

  ext4_show_stats((const struct ext4_super_block *)ext4_info.sb,
                  ext4_info.bg_groups,
                  (const struct ext4_group_desc_min *)ext4_info.bg_desc);

  return 0;
}

static int32_t fs_do_stat(int32_t argc, const char **argv)
{
  int32_t ino = EXT4_UNUSED_INO;
  struct ext4_inode inode;
  int32_t ret = 0;

  if (argc != 2 || argv == NULL) {
    error("invalid ext4 args!");
    return -1;
  }

  /*
   * Parse args
   * e.g., 'stat name' or 'stat <ino>'
   */
  ret = fs_parse_ino(argv[1], &ino);
  if (ret != 0) {
    ret = fs_name2ino(argv[1],
                      ext4_info.cwd.dentries,
                      (const struct ext4_dir_entry_2 *)ext4_info.cwd.dentry,
                      &ino);
    if (ret != 0) {
      error("invalid ext4 args!");
      return -1;
    }
  }

  /*
   * Fill in Ext4 inode
   */
  memset((void *)&inode, 0, sizeof(struct ext4_inode));

  ret = ext4_fill_inode((const struct ext4_super_block *)ext4_info.sb,
                        (const struct ext4_group_desc_min *)ext4_info.bg_desc,
                        ino,
                        &inode);
  if (ret != 0) {
    error("failed to stat ext4 filesystem!");
    return -1;
  }

  /*
   * Show Ext4 inode stat
   */
  ext4_show_inode_stat((const struct ext4_super_block *)ext4_info.sb,
                       ino,
                       (const struct ext4_inode *)&inode);

  return 0;
}

static int32_t fs_do_pwd(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  if (0 == strlen(ext4_info.cwd.path)) {
    fprintf(stdout, "%s\n", ext4_info.cwd.root);    
  } else {
    fprintf(stdout, "%s\n", ext4_info.cwd.path);
  }

  return 0;
}

static int32_t fs_do_cd(int32_t argc, const char **argv)
{
  const char *name = NULL;
  int32_t ino = EXT4_UNUSED_INO;
  int32_t ret = 0;

  if (argc != 2 || argv == NULL) {
    error("invalid ext4 args!");
    return -1;
  }

  name = argv[1];
  if (name == NULL) {
    error("invalid ext4 args!");
    return -1;
  }

  /*
   * Parse args
   */
  ret = fs_name2ino(name,
                    ext4_info.cwd.dentries,
                    (const struct ext4_dir_entry_2 *)ext4_info.cwd.dentry,
                    &ino);
  if (ret != 0) {
    error("invalid ext4 args!");
    return -1;
  }

  /*
   * Fill in Ext4 dentry list
   */
  ret = fs_ino2dentry(ino,
                      (const struct ext4_super_block *)ext4_info.sb,
                      (const struct ext4_group_desc_min *)ext4_info.bg_desc,
                      &ext4_info.cwd.dentries,
                      &ext4_info.cwd.dentry);
  if (ret != 0) {
    error("failed to change ext4 directory!");
    return -1;
  }

  /*
   * Update Ext4 info
   */
  ext4_info.cwd.ino = ino;

  if (strlen(name) == strlen(FS_CURRENT_PATH) && 0 == strncmp(name, FS_CURRENT_PATH, strlen(name))) {
    return 0;
  }

  if (strlen(name) == strlen(FS_UPPER_PATH) && 0 == strncmp(name, FS_UPPER_PATH, strlen(name))) {
    ret = fs_path_pop(ext4_info.cwd.path);
    if (ret != 0) {
      error("failed to change ext4 directory!");
      return -1;
    }

    return 0;
  }

  ret = fs_path_push(name, ext4_info.cwd.path);
  if (ret != 0) {
    error("failed to change ext4 directory!");
    return -1;
  }

  return 0;
}

static int32_t fs_do_ls(int32_t argc, const char **argv)
{
  int32_t i = 0, j = 0;

  argc = argc;
  argv = argv;

  for (i = 0; i < ext4_info.cwd.dentries; ++i) {
    fprintf(stdout, "<%u>", ext4_info.cwd.dentry[i].inode);

    for (j = 0; j < ext4_info.cwd.dentry[i].name_len; ++j) {
      fprintf(stdout, "%c", ext4_info.cwd.dentry[i].name[j]);
    }

    fprintf(stdout, "  ");
  }
  fprintf(stdout, "\n");

  return 0;
}

static int32_t fs_do_mkdir(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  return -1;
}

static int32_t fs_do_rm(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  return -1;
}

static int32_t fs_do_read(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  return -1;
}

static int32_t fs_do_write(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  return -1;
}
