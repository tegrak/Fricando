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
#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif
#ifdef HAVE_FCNTL_H
#include <fcntl.h>
#endif
#ifdef HAVE_STRING_H
#include <string.h>
#endif
#ifdef HAVE_SYS_TYPES_H
#include <sys/types.h>
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
#ifndef O_BINARY
#define O_BINARY  (0)
#endif

#define FS_FAT_PATH_LEN_MAX  (255)

#define FS_FAT_REDIRECT_CMD  ">"

/*
 * Type Definition
 */
typedef struct {
  const char *root;
  char path[FS_FAT_PATH_LEN_MAX + 1];
  int32_t dentries;
  struct msdos_dir_slot *dslot;
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
static int32_t fs_root2dentry(const struct fat_super_block *sb, int32_t *dentries, struct msdos_dir_slot **dslot, struct msdos_dir_entry **dentry);
static int32_t fs_clus2dentry(int32_t cluster, const struct fat_super_block *sb, int32_t *dentries, struct msdos_dir_slot **dslot, struct msdos_dir_entry **dentry);
static int32_t fs_name2dentry(const char *name, int32_t dentries, const struct msdos_dir_entry *dentry, struct msdos_dir_entry *entry);
static int32_t fs_path_push(const char *dirname, char *path);
static int32_t fs_path_pop(char *path);
static int32_t fs_output_stdout(const uint8_t *buf, size_t size);
static int32_t fs_output_file(const uint8_t *buf, size_t size, const char *name);

static int32_t fs_do_mount(int32_t argc, const char **argv);
static int32_t fs_do_umount(int32_t argc, const char **argv);
static int32_t fs_do_stats(int32_t argc, const char **argv);
static int32_t fs_do_stat(int32_t argc, const char **argv);
static int32_t fs_do_pwd(int32_t argc, const char **argv);
static int32_t fs_do_cd(int32_t argc, const char **argv);
static int32_t fs_do_ls(int32_t argc, const char **argv);
static int32_t fs_do_mkdir(int32_t argc, const char **argv);
static int32_t fs_do_rm(int32_t argc, const char **argv);
static int32_t fs_do_cat(int32_t argc, const char **argv);
static int32_t fs_do_echo(int32_t argc, const char **argv);

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
    .opt_hdl = fs_do_cat,
    .opt_cmd = "cat",
  },

  [10] = {
    .opt_hdl = fs_do_echo,
    .opt_cmd = "echo",
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
static int32_t fs_root2dentry(const struct fat_super_block *sb, int32_t *dentries, struct msdos_dir_slot **dslot, struct msdos_dir_entry **dentry)
{
  int32_t dentries_new = 0;
  int32_t ret = 0;

  if (sb == NULL || dentries == NULL || dslot == NULL || dentry == NULL) {
    return -1;
  }

  ret = fat_fill_root_dentries(sb, &dentries_new);
  if (ret != 0) {
    return -1;
  }

  if (dentries_new > *dentries) {
    *dslot = (struct msdos_dir_slot *)realloc((void *)*dslot, sizeof(struct msdos_dir_slot) * dentries_new);
    if (*dslot == NULL) {
      return -1;
    }
    memset((void *)*dslot, 0, sizeof(struct msdos_dir_slot) * dentries_new);

    *dentry = (struct msdos_dir_entry *)realloc((void *)*dentry, sizeof(struct msdos_dir_entry) * dentries_new);
    if (*dentry == NULL) {
      return -1;
    }
    memset((void *)*dentry, 0, sizeof(struct msdos_dir_entry) * dentries_new);
  }

  *dentries = dentries_new;

  ret = fat_fill_root_dentry(sb, *dentries, *dslot, *dentry);
  if (ret != 0) {
    return -1;
  }

  return 0;
}

static int32_t fs_clus2dentry(int32_t cluster, const struct fat_super_block *sb, int32_t *dentries, struct msdos_dir_slot **dslot, struct msdos_dir_entry **dentry)
{
  int32_t dentries_new = 0;
  int32_t ret = 0;

  if (cluster < FAT_START_ENT || sb == NULL || dentries == NULL || dslot == NULL || dentry == NULL) {
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
    *dslot = (struct msdos_dir_slot *)realloc((void *)*dslot, sizeof(struct msdos_dir_slot) * dentries_new);
    if (*dslot == NULL) {
      return -1;
    }
    memset((void *)*dslot, 0, sizeof(struct msdos_dir_slot) * dentries_new);

    *dentry = (struct msdos_dir_entry *)realloc((void *)*dentry, sizeof(struct msdos_dir_entry) * dentries_new);
    if (*dentry == NULL) {
      return -1;
    }
    memset((void *)*dentry, 0, sizeof(struct msdos_dir_entry) * dentries_new);
  }

  *dentries = dentries_new;

  ret = fat_fill_dentry(sb, cluster, *dentries, *dslot, *dentry);
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

      if (0 != len_ext && 0 == strncmp(name + len_base + 1, ext, len_ext)) {
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

static int32_t fs_path_push(const char *dirname, char *path)
{
  size_t len_path = 0, len_name;
  char *ptr = NULL;

  if (dirname == NULL || path == NULL) {
    return -1;
  }

  len_path = strlen(path);
  len_name = strlen(dirname);

  if ((FS_FAT_PATH_LEN_MAX + 1 - len_path) < (strlen(FS_PATH_DELIM) + len_name + 1)) {
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

static int32_t fs_output_stdout(const uint8_t *buf, size_t size)
{
  size_t i = 0;

  if (buf == NULL || size == 0) {
    return -1;
  }

  for (i = 0; i < size; ++i) {
    fprintf(stdout, "%c", buf[i]);
  }
  fprintf(stdout, "\n");

  return 0;
}

static int32_t fs_output_file(const uint8_t *buf, size_t size, const char *name)
{
  int32_t fd = 0;
  int32_t ret = 0;

  if (buf == NULL || size == 0 || name == NULL) {
    return -1;
  }

  ret = access(name, F_OK);
  if (ret != 0) {
    return -1;
  }

  ret = access(name, W_OK);
  if (ret != 0) {
    return -1;
  }

  fd = open(name, O_WRONLY | O_BINARY);
  if (fd < 0) {
    return -1;
  }

  ret = lseek(fd, 0, SEEK_SET);
  if (ret < 0) {
    ret = -1;
    goto fs_output_file_done;
  }

  ret = write(fd, (const void *)buf, size);
  if (ret < 0) {
    ret = -1;
    goto fs_output_file_done;
  }

  ret = 0;

 fs_output_file_done:

  close(fd);

  return ret;
}

static int32_t fs_do_mount(int32_t argc, const char **argv)
{
  const char *name = NULL;
  struct fat_super_block *sb = NULL;
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
  fat_info.cwd.root = FS_ROOT_PATH;
  memset((void *)fat_info.cwd.path, 0, FS_FAT_PATH_LEN_MAX + 1);
  fat_info.cwd.dentries = 0;
  fat_info.cwd.dslot = NULL;
  fat_info.cwd.dentry = NULL;
  fat_info.sb = sb;

  /*
   * Fill in FAT dentry list
   */
  ret = fs_root2dentry((const struct fat_super_block *)fat_info.sb,
                       &fat_info.cwd.dentries,
                       &fat_info.cwd.dslot,
                       &fat_info.cwd.dentry);
  if (ret != 0) {
    goto fs_do_mount_fail;
  }

  return 0;

 fs_do_mount_fail:

  if (fat_info.cwd.dentry != NULL) {
    free(fat_info.cwd.dentry);
    fat_info.cwd.dentry = NULL;
  }

  if (fat_info.cwd.dslot != NULL) {
    free(fat_info.cwd.dslot);
    fat_info.cwd.dslot = NULL;
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

  if (fat_info.cwd.dslot != NULL) {
    free(fat_info.cwd.dslot);
    fat_info.cwd.dslot = NULL;
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

  if (0 == strlen(fat_info.cwd.path)) {
    fprintf(stdout, "%s\n", fat_info.cwd.root);    
  } else {
    fprintf(stdout, "%s\n", fat_info.cwd.path);
  }

  return 0;
}

static int32_t fs_do_cd(int32_t argc, const char **argv)
{
  const char *name = NULL;
  struct msdos_dir_entry entry;
  int32_t status = 0;
  int32_t cluster = 0;
  size_t size = 0;
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
   * Check if dentry refers to directory
   */
  ret = fat_dent_attr_is_dir((const struct msdos_dir_entry *)&entry, &status);
  if (ret != 0 || status == 0) {
    error("failed to change fat directory!");
    return -1;
  }

  /*
   * Fill in FAT dentry list
   */
  ret = fat_fill_dent_start((const struct fat_super_block *)fat_info.sb,
                            (const struct msdos_dir_entry *)&entry,
                            &cluster,
                            &size);
  if (ret != 0) {
    error("failed to change fat directory!");
    return -1;
  }

  if (cluster == FAT_ENT_FREE) {
    /*
     * Change to root directory
     * if start clust = 0 in dentry of '..'
     */
    ret = fs_root2dentry((const struct fat_super_block *)fat_info.sb,
                         &fat_info.cwd.dentries,
                         &fat_info.cwd.dslot,
                         &fat_info.cwd.dentry);
  } else {
    ret = fs_clus2dentry(cluster,
                         (const struct fat_super_block *)fat_info.sb,
                         &fat_info.cwd.dentries,
                         &fat_info.cwd.dslot,
                         &fat_info.cwd.dentry);
  }

  if (ret != 0) {
    error("failed to change fat directory!");
    return -1;
  }

  /*
   * Update FAT info
   */
  if (strlen(name) == strlen(FS_CURRENT_PATH) && 0 == strncmp(name, FS_CURRENT_PATH, strlen(name))) {
    return 0;
  }

  if (strlen(name) == strlen(FS_UPPER_PATH) && 0 == strncmp(name, FS_UPPER_PATH, strlen(name))) {
    ret = fs_path_pop(fat_info.cwd.path);
    if (ret != 0) {
      error("failed to change fat directory!");
      return -1;
    }

    return 0;
  }

  ret = fs_path_push(name, fat_info.cwd.path);
  if (ret != 0) {
    error("failed to change fat directory!");
    return -1;
  }

  return 0;
}

static int32_t fs_do_ls(int32_t argc, const char **argv)
{
  int32_t i = 0, j = 0;
  const char *base = NULL, *ext = NULL;

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

static int32_t fs_do_cat(int32_t argc, const char **argv)
{
  const char *name_in = NULL, *name_out = NULL;
  struct msdos_dir_entry entry;
  int32_t status = 0;
  int32_t cluster = 0;
  size_t size = 0;
  uint8_t *buf = NULL;
  int32_t ret = 0;

  /*
   * Support for commands of 'cat file' (argc = 2)
   * and 'cat srd_file > dst_file' (argc = 4)
   */
  if ((argc != 2 && argc != 4)
      || argv == NULL) {
    error("invalid fat args!");
    return -1;
  }

  name_in = argv[1];
  if (name_in == NULL) {
    error("invalid fat args!");
    return -1;
  }

  if (argc == 4) {
    if (strlen(argv[2]) != strlen(FS_FAT_REDIRECT_CMD)) {
      error("invalid fat args!");
      return -1;
    }

    if (0 != strncmp(argv[2], FS_FAT_REDIRECT_CMD, strlen(FS_FAT_REDIRECT_CMD))) {
      error("invalid fat args!");
      return -1;
    }

    name_out = argv[3];
    if (name_out == NULL) {
      error("invalid fat args!");
      return -1;
    }
  }

  /*
   * Parse args
   */
  memset((void *)&entry, 0, sizeof(struct msdos_dir_entry));

  ret = fs_name2dentry(name_in, fat_info.cwd.dentries, (const struct msdos_dir_entry *)fat_info.cwd.dentry, &entry);
  if (ret != 0) {
    error("failed to cat fat file!");
    return -1;
  }

  /*
   * Check if dentry refers to directory
   */
  ret = fat_dent_attr_is_dir((const struct msdos_dir_entry *)&entry, &status);
  if (ret != 0 || status == 1) {
    error("failed to cat fat file!");
    return -1;
  }

  /*
   * Fill in FAT file buffer
   */
  ret = fat_fill_dent_start((const struct fat_super_block *)fat_info.sb,
                            (const struct msdos_dir_entry *)&entry,
                            &cluster,
                            &size);
  if (ret != 0) {
    error("failed to cat fat file!");
    return -1;
  }

  if (cluster < FAT_START_ENT) {
    error("failed to cat fat file!");
    return -1;
  }

  if (size == 0) {
    return 0;
  }

  buf = (uint8_t *)malloc(size);
  if (buf == NULL) {
    error("failed to cat fat file!");
    return -1;
  }
  memset((void *)buf, 0, size);

  ret = fat_fill_file((const struct fat_super_block *)fat_info.sb, cluster, size, buf);
  if (ret != 0) {
    error("failed to cat fat file!");
    goto fs_do_cat_done;
  }

  /*
   * Output file buffer
   */
  if (name_out != NULL) {
    /*
     * Outputed to file
     */
    ret = fs_output_file((const uint8_t *)buf, size, name_out);
  } else {
    /*
     * Outputed to standard output
     */
    ret = fs_output_stdout((const uint8_t *)buf, size);
  }

  if (ret != 0) {
    error("failed to cat fat file!");
    goto fs_do_cat_done;
  }

  ret = 0;

 fs_do_cat_done:

  if (buf != NULL) {
    free(buf);
    buf = NULL;
  }

  return ret;
}

static int32_t fs_do_echo(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  return -1;
}
