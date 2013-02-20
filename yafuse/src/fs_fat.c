/**
 * fs_fat.c - The entry of FAT filesystem.
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
#include "include/libfat/msdos_fs.h"
#include "include/libfat/libfat.h"
#include "include/libio/io.h"

#include "filesystem.h"
#include "fs_fat.h"

/*
 * Macro Definition
 */
#define FS_FAT_PATH_LEN_MAX  (255)

/*
 * Type Definition
 */
typedef struct {
  int32_t cluster;
  char path[FS_FAT_PATH_LEN_MAX + 1];
  int32_t dentries;
  struct msdos_dir_entry *dentry;
} fs_fat_cwd_t;

typedef struct {
  /*
   * General info
   */
  fs_fat_cwd_t cwd;

  /*
   * Filesystem info
   */
  struct fat_super_block *sb;
} fs_fat_info_t;

/*
 * Function Declaration
 */
static int32_t fs_root2dentry(const struct fat_super_block *sb, int32_t *dentries, struct msdos_dir_entry **dentry);
static int32_t fs_clus2dentry(int32_t cluster, const struct fat_super_block *sb, int32_t *dentries, struct msdos_dir_entry **dentry);
static int32_t fs_name2dentry(const char *name, int32_t dentries, const struct msdos_dir_entry *dentry, struct msdos_dir_entry *entry);
static int32_t fs_update_path(const char *dirname, char *path);

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
 * FAT filesystem operation table
 */
fs_opt_t fs_opt_tbl_fat[FS_OPT_TBL_NUM_MAX] = {
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

static fs_fat_info_t fat_info;

/*
 * Function Definition
 */
static int32_t fs_root2dentry(const struct fat_super_block *sb, int32_t *dentries, struct msdos_dir_entry **dentry)
{
  int32_t dentries_new = 0;
  int32_t ret = 0;

  if (sb == NULL || dentries == NULL || dentry == NULL) {
    return -1;
  }

  ret = fat_fill_root_dentries(sb, &dentries_new);
  if (ret != 0) {
    return -1;
  }

  if (dentries_new > *dentries) {
    *dentry = (struct msdos_dir_entry *)realloc((void *)*dentry, sizeof(struct msdos_dir_entry) * dentries_new);
    if (*dentry == NULL) {
      return -1;
    }
    memset((void *)*dentry, 0, sizeof(struct msdos_dir_entry) * dentries_new);
  }

  *dentries = dentries_new;

  ret = fat_fill_root_dentry(sb, *dentries, *dentry);
  if (ret != 0) {
    return -1;
  }

  return 0;
}

static int32_t fs_clus2dentry(int32_t cluster, const struct fat_super_block *sb, int32_t *dentries, struct msdos_dir_entry **dentry)
{
  int32_t dentries_new = 0;
  int32_t ret = 0;

  if (cluster < FAT_START_ENT
      || sb == NULL
      || dentries == NULL
      || dentry == NULL
      || *dentry == NULL) {
    return -1;
  }

  /*
   * Fill in FAT dentries
   */
  ret = fat_fill_dentries(sb, cluster, &dentries_new);
  if (ret != 0) {
    return -1;
  }

  /*
   * Fill in FAT dentry list
   */
  if (dentries_new > *dentries) {
    *dentry = (struct msdos_dir_entry *)realloc((void *)*dentry, sizeof(struct msdos_dir_entry) * dentries_new);
    if (*dentry == NULL) {
      return -1;
    }
    memset((void *)*dentry, 0, sizeof(struct msdos_dir_entry) * dentries_new);
  }

  *dentries = dentries_new;

  ret = fat_fill_dentry(sb, cluster, *dentries, *dentry);
  if (ret != 0) {
    return -1;
  }

  return 0;
}

static int32_t fs_name2dentry(const char *name, int32_t dentries, const struct msdos_dir_entry *dentry, struct msdos_dir_entry *entry)
{
  int32_t i = 0, j = 0;
  size_t len_name = 0, len_base = 0, len_ext = 0;
  const char *base = NULL,  *ext = NULL;
  int32_t ret = -1;

  if (name == NULL
      || dentries == 0
      || dentry == NULL
      || entry == NULL) {
    return -1;
  }

  len_name = strlen(name);

  if (len_name >= MSDOS_NAME) {
    return -1;
  }

  for (i = 0; i < dentries; ++i) {
    base = (const char *)dentry[i].name;
    ext = (const char *)dentry[i].name + MSDOS_NAME_BASE_LEN;

    for (j = 0; j < MSDOS_NAME_BASE_LEN; ++j) {
      if (base[j] == '\0' || base[j] == 0x20) {
        break;
      }
    }

    len_base = j;

    if (len_base <= len_name) {
      if (0 != strncmp(name, base, len_base)) {
        continue;
      }

      if (len_base < len_name && name[len_base] != '.') {
        continue;
      }

      for (j = 0; j < MSDOS_NAME_EXT_LEN; ++j) {
        if (ext[j] == '\0' || ext[j] == 0x20) {
          break;
        }
      }

      len_ext = j;

      if (len_base == len_name && len_ext == 0) {
        ret = 0;
        break;
      }

      if (len_ext != (len_name - len_base - 1)) {
        continue;
      }

      if (0 == strncmp(name + len_base + 1, ext, len_ext)) {
        ret = 0;
        break;
      }
    }
  }

  if (ret == 0) {
    memcpy((void *)entry, (const void *)&dentry[i], sizeof(struct msdos_dir_entry));
  }

  return ret;
}

static int32_t fs_update_path(const char *dirname, char *path)
{
  const char *buf = NULL;
  char *ptr = NULL;
  int32_t len = 0, len_s1 = 0, len_s2 = 0;

  if (dirname == NULL || path == NULL) {
    return -1;
  }

  /*
   * Ignore '/' in path if '//' occurs
   */
  len_s1 = strlen(FS_PATH_DELIM);
  len_s2 = strlen(dirname);

  if (len_s1 == len_s2) {
    if (0 == strncmp(dirname, FS_PATH_DELIM, len_s1)) {
      len_s2 = strlen(path);
      if (len_s1 == len_s2) {
        if (0 == strncmp(path, FS_PATH_DELIM, len_s1)) {
          return 0;
        }
      }
    }
  }

  /*
   * Ignore dirname of '.'
   */
  len_s1 = strlen(FS_CURRENT_PATH);
  len_s2 = strlen(dirname);

  if (len_s1 == len_s2) {
    if (0 == strncmp(dirname, FS_CURRENT_PATH, len_s1)) {
      return 0;
    }
  }

  /*
   * Remove current dir name in path if dirname is '..'
   */
  len_s1 = strlen(FS_UPPER_PATH);
  len_s2 = strlen(dirname);

  if (len_s1 == len_s2) {
    if (0 == strncmp(dirname, FS_UPPER_PATH, len_s1)) {
      buf = FS_PATH_DELIM;

      ptr = strrchr((const char *)path, buf[0]);
      if (ptr == NULL) {
        return 0;
      } else if (ptr == path) {
        memset(ptr + 1, 0, strlen(ptr + 1));
      } else {
        memset(ptr, 0, strlen(ptr));
      }

      ptr = strrchr((const char *)path, buf[0]);
      if (ptr == NULL) {
        return 0;
      } else if (ptr == path) {
        memset(ptr + 1, 0, strlen(ptr + 1));
      } else {
        memset(ptr, 0, strlen(ptr));
      }

      return 0;
    }
  }

  /*
   * Concatenate path and dirname
   */
  len = strlen(path) + strlen(dirname);

  if (len <= FS_FAT_PATH_LEN_MAX) {
    strncat(path, dirname, strlen(dirname));
  } 

  return 0;
}

static int32_t fs_do_mount(int32_t argc, const char **argv)
{
  const char *name = NULL;
  struct fat_super_block *sb = NULL;
  int32_t is_fat32_fs = 0;
  int32_t ret = -1;

  if (argc < 2 || argv == NULL) {
    error("invalid fat args!");
    return -1;
  }

  name = argv[1];
  if (name == NULL) {
    error("invalid fat args!");
    return -1;
  }

  /*
   * Open FAT image
   */
  ret = io_open(name);
  if (ret != 0) {
    error("failed to open fat io!");
    return -1;
  }

  /*
   * Fill in FAT superblock
   */
  sb = (struct fat_super_block *)malloc(sizeof(struct fat_super_block));
  if (sb == NULL) {
    error("failed to malloc fat sb!");
    ret = -1;
    goto fs_do_mount_fail;
  }
  memset((void *)sb, 0, sizeof(struct fat_super_block));

  ret = fat_fill_sb(sb);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  /*
   * Init FAT info
   */
  fat_info.cwd.cluster = FAT_START_ENT;

  memset((void *)fat_info.cwd.path, 0, FS_FAT_PATH_LEN_MAX + 1);
  ret = fs_update_path(FS_ROOT_PATH, fat_info.cwd.path);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  fat_info.cwd.dentries = 0;
  fat_info.cwd.dentry = NULL;
  fat_info.sb = sb;

  /*
   * Check FAT type
   */
  ret = fat_is_fat32_fs((const struct fat_super_block *)sb, &is_fat32_fs);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  /*
   * Fill in FAT dentry list
   */
  if (is_fat32_fs) {
    ret = fs_clus2dentry(fat_info.cwd.cluster,
                         (const struct fat_super_block *)fat_info.sb,
                         &fat_info.cwd.dentries,
                         &fat_info.cwd.dentry);
  } else {
    ret = fs_root2dentry((const struct fat_super_block *)fat_info.sb,
                         &fat_info.cwd.dentries,
                         &fat_info.cwd.dentry);
  }

  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  return 0;

 fs_do_mount_fail:

  if (fat_info.cwd.dentry != NULL) {
    free(fat_info.cwd.dentry);
    fat_info.cwd.dentry = NULL;
  }

  if (sb != NULL) {
    free(sb);
    sb = NULL;
  }

  io_close();

  memset((void *)&fat_info, 0, sizeof(fs_fat_info_t));

  return ret;
}

static int32_t fs_do_umount(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  if (fat_info.cwd.dentry != NULL) {
    free(fat_info.cwd.dentry);
    fat_info.cwd.dentry = NULL;
  }

  if (fat_info.sb != NULL) {
    free(fat_info.sb);
    fat_info.sb = NULL;
  }

  io_close();

  memset((void *)&fat_info, 0, sizeof(fs_fat_info_t));

  return 0;
}

static int32_t fs_do_stats(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  if (fat_info.sb == NULL) {
    error("failed to stats fat filesystem!");
    return -1;
  }

  fat_show_stats((const struct fat_super_block *)fat_info.sb);

  return 0;
}

static int32_t fs_do_stat(int32_t argc, const char **argv)
{
  const char *name = NULL;
  struct msdos_dir_entry entry;
  int32_t ret = 0;

  if (argc != 2 || argv == NULL) {
    error("invalid fat args!");
    return -1;
  }

  name = argv[1];
  if (name == NULL) {
    error("invalid fat args!");
    return -1;
  }

  memset((void *)&entry, 0, sizeof(struct msdos_dir_entry));

  ret = fs_name2dentry(name, fat_info.cwd.dentries, (const struct msdos_dir_entry *)fat_info.cwd.dentry, &entry);
  if (ret != 0) {
    error("failed to stat fat filesystem!");
    return -1;
  }

  fat_show_dentry((const struct fat_super_block *)fat_info.sb, (const struct msdos_dir_entry *)&entry);

  return 0;
}

static int32_t fs_do_pwd(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  fprintf(stdout, "%s\n", fat_info.cwd.path);

  return 0;
}

static int32_t fs_do_cd(int32_t argc, const char **argv)
{
  const char *name = NULL;
  struct msdos_dir_entry entry;
  int32_t start_cluster = 0;
  int32_t ret = 0;

  if (argc != 2 || argv == NULL) {
    error("invalid fat args!");
    return -1;
  }

  name = argv[1];
  if (name == NULL) {
    error("invalid fat args!");
    return -1;
  }

  /*
   * Parse args
   */
  memset((void *)&entry, 0, sizeof(struct msdos_dir_entry));

  ret = fs_name2dentry(name, fat_info.cwd.dentries, (const struct msdos_dir_entry *)fat_info.cwd.dentry, &entry);
  if (ret != 0) {
    error("failed to change fat directory!");
    return -1;
  }

  /*
   * Fill in FAT dentry list
   */
  ret = fat_fill_dent_start((const struct fat_super_block *)fat_info.sb,
                            (const struct msdos_dir_entry *)&entry,
                            &start_cluster);
  if (ret != 0) {
    error("failed to change fat directory!");
    return -1;
  }

  ret = fs_clus2dentry(start_cluster,
                       (const struct fat_super_block *)fat_info.sb,
                       &fat_info.cwd.dentries,
                       &fat_info.cwd.dentry);
  if (ret != 0) {
    error("failed to change fat directory!");
    return -1;
  }

  /*
   * Update FAT info
   */
  fat_info.cwd.cluster = start_cluster;

  ret = fs_update_path(FS_PATH_DELIM, fat_info.cwd.path);
  if (ret != 0) {
    error("failed to change fat directory!");
    return -1;
  }

  ret = fs_update_path(name, fat_info.cwd.path);
  if (ret != 0) {
    error("failed to change fat directory!");
    return -1;
  }

  return 0;
}

static int32_t fs_do_ls(int32_t argc, const char **argv)
{
  int32_t i = 0, j = 0;
  const char *base = NULL,  *ext = NULL;

  argc = argc;
  argv = argv;

  for (i = 0; i < fat_info.cwd.dentries; ++i) {
    base = (const char *)fat_info.cwd.dentry[i].name;
    ext = (const char *)fat_info.cwd.dentry[i].name + MSDOS_NAME_BASE_LEN;

    for (j = 0; j < MSDOS_NAME_BASE_LEN; ++j) {
      if (base[j] == '\0' || base[j] == 0x20) {
        break;
      }
      fprintf(stdout, "%c", base[j]);
    }

    if (ext[0] != '\0' && ext[0] != 0x20) {
      fprintf(stdout, ".");

      for (j = 0; j < MSDOS_NAME_EXT_LEN; ++j) {
        fprintf(stdout, "%c", ext[j]);
      }
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
