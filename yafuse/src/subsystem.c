/**
 * subsystem.c - The entry of subsystem.
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
#ifdef HAVE_READLINE_READLINE_H
#include <readline/readline.h>
#endif

#ifdef DEBUG
// Add code here
#endif

#include "subsystem.h"
#include "filesystem.h"

/*
 * Macro Definition
 */
#define SS_OPT_TBL_NUM_MAX  (20)

#define SS_PROMPT_DEFAULT  "$ "
#define SS_PROMPT_DEFAULT_LEN  (2)

#define SS_HISTORY_BUF_LEN  (20)

/*
 * Type Definition
 */
typedef struct {
  int32_t abort;
} ss_data_t;

/*
 * Function Declaration
 */
static int32_t help_ss(int32_t argc, char **argv);
static int32_t history_ss(int32_t argc, char **argv);
static int32_t quit_ss(int32_t argc, char **argv);

static void ss_add_history(const char *line);
static void ss_auto_completion();
static fs_opt_handle_t ss_opt_hdl_match(const char *opt_cmd);
static void ss_exec_line(int32_t fs_idx, const char *line);
static void ss_listen(const char *ss_prompt, const char *fs_name);

/*
 * Global Variable Definition
 */
extern fs_opt_t fs_opt_tbl_ext4[];
extern fs_opt_t fs_opt_tbl_fat32[];

static ss_data_t ss_data;

static fs_opt_t ss_opt_tbl[SS_OPT_TBL_NUM_MAX] = {
  [0] = {
    .opt_hdl = help_ss,
    .opt_cmd = "help",
  },

  [1] = {
    .opt_hdl = history_ss,
    .opt_cmd = "history",
  },

  [2] = {
    .opt_hdl = quit_ss,
    .opt_cmd = "quit",
  },
};

static const char* ss_history_buf[SS_HISTORY_BUF_LEN];
static int32_t ss_history_buf_idx;

/*
 * Function Definition
 */
static int32_t help_ss(int32_t argc, char **argv)
{
  int32_t opt_num = 0;
  const char *opt_cmd = NULL;
  int32_t i = 0;
  int32_t fs_idx = -1;

  fprintf(stdout, "command list: ");

  for (i = 0; i < SS_OPT_TBL_NUM_MAX; ++i) {
    if (ss_opt_tbl[i].opt_hdl != NULL) {
      fprintf(stdout, "%s ", ss_opt_tbl[i].opt_cmd);
    } else {
      break;
    }
  }

  if (argc > 0 && argv != NULL) {
    fs_idx = atoi(argv[0]);
    if (fs_idx >= 0 && fs_idx < FS_TYPE_NUM_MAX) {
      opt_num = fs_opt_num(fs_idx);
      for (i = 0; i < opt_num; ++i) {
	opt_cmd = fs_opt_cmd_enum(fs_idx, i);
	fprintf(stdout, "%s ", opt_cmd);
      }
    }
  }

  fprintf(stdout, "\n");

  return 0;
}

static int32_t history_ss(int32_t argc, char **argv)
{
  int32_t index = 0;
  int32_t i = 0, j = 0;

  index = ss_history_buf_idx % SS_HISTORY_BUF_LEN;

  for (i = 0, j = 0; i < SS_HISTORY_BUF_LEN; ++i, ++index) {
    index %= SS_HISTORY_BUF_LEN;
    if (ss_history_buf[index] != NULL) {
      fprintf(stdout, "%d  %s\n", j++, ss_history_buf[index]);
    }
  }

  return 0;
}

static int32_t quit_ss(int32_t argc, char **argv)
{
  ss_data.abort = 1;

  return 0;
}

/*
 * Add subsystem command to command history
 */
static void ss_add_history(const char *line)
{
  if (line == NULL || strlen(line) == 0) {
    return;
  }

  ss_history_buf_idx %= SS_HISTORY_BUF_LEN;
  ss_history_buf[ss_history_buf_idx++] = line;
}

/*
 * Auto completion for subsystem command
 */
static void ss_auto_completion()
{
}

/*
 * Match opt handle with opt command
 */
static fs_opt_handle_t ss_opt_hdl_match(const char *opt_cmd)
{
  int32_t i = 0;
  int32_t len_0 = 0, len_1 = 0;
  fs_opt_handle_t handle = NULL;

  if (opt_cmd == NULL) {
    return NULL;
  }

  len_1 = strlen(opt_cmd);

  for (i = 0; i < SS_OPT_TBL_NUM_MAX; ++i) {
    if (ss_opt_tbl[i].opt_cmd != NULL) {
      len_0 = strlen(ss_opt_tbl[i].opt_cmd);
    } else {
      len_0 = 0;
    }

    if (len_0 > 0 && len_0 <= len_1) {
      if (strncmp(ss_opt_tbl[i].opt_cmd, opt_cmd, len_0) == 0) {
        handle = ss_opt_tbl[i].opt_hdl;
        break;
      }
    }
  }

  return handle;
}

/*
 * Execute command line for filesystem
 */
static void ss_exec_line(int32_t fs_idx, const char *line)
{
  fs_opt_handle_t handle = NULL;
  int32_t argc = 0;
  char *argv = NULL;
  int32_t ret = -1;

  handle = fs_opt_hdl_match(fs_idx, line);
  if (handle != NULL) {
    argc = 1;
    argv = (char *)line;
    ret = handle(argc, (char **)&argv);
  } else {
    handle = ss_opt_hdl_match(line);
    if (handle != NULL) {
      argc = 1;
      argv = (char *)malloc(argc * 6);
      snprintf(argv, sizeof(argv), "%d", fs_idx);
      ret = handle(argc, (char **)&argv);
      free(argv);
    }
  }

  if (ret != 0) {
    fprintf(stdout, "press 'help' for more info.\n");
  }
}

/*
 * Listen for reading line in subsystem
 */
static void ss_listen(const char *ss_prompt, const char *fs_name)
{
  int32_t fs_idx = -1;
  const char *line = NULL;

  /*
   * Open filesystem
   */
  if (fs_name != NULL) {
    fs_idx = fs_open(fs_name);
  }

  ss_data.abort = 0;

  /*
   * Read line
   */
  while (ss_data.abort == 0) {
    line = readline((const char *)ss_prompt);

    if (line != NULL && strlen(line) > 0) {
      ss_add_history(line);
      ss_exec_line(fs_idx, line);
    }
  }
}

/*
 * Create subsystem
 */
int32_t ss_create(const char *ss_name, const char *fs_name, int32_t *ret_val)
{
  char ss_prompt[SS_NAME_LEN_MAX + SS_PROMPT_DEFAULT_LEN + 1] = {0};
  int32_t ss_prompt_len = 0;
  int32_t ret = 0;

  if (ret_val == NULL) {
    fprintf(stderr, "ERROR: invalid args!\n");
    return -1;
  }

  /*
   * Display banner
   */
  fprintf(stdout, "WELCOME TO YAFUSE!\n");
  fprintf(stdout, "press 'help' for more info.\n");

  /*
   * Register filesystem
   */
  ret = fs_register(fs_opt_tbl_ext4);
  if (ret != 0) {
    fprintf(stderr, "WARNING: failed to register Ext4 operation table!\n");
  }

  ret = fs_register(fs_opt_tbl_fat32);
  if (ret != 0) {
    fprintf(stderr, "WARNING: failed to register FAT32 operation table!\n");
  }

  if (ss_name == NULL) {
    strncpy((void *)ss_prompt, SS_PROMPT_DEFAULT, strlen(SS_PROMPT_DEFAULT));
  } else {
    ss_prompt_len = (strlen(ss_name) >= SS_NAME_LEN_MAX) ? SS_NAME_LEN_MAX : strlen(ss_name);
    strncpy((void *)ss_prompt, ss_name, ss_prompt_len);
    strncat((void *)ss_prompt, SS_PROMPT_DEFAULT, SS_PROMPT_DEFAULT_LEN);
  }

  /*
   * Listener for reading line in subsystem
   */
  ss_listen((const char *)ss_prompt, fs_name);

  return 0;
}

/*
 * Delete subsystem
 */
void ss_delete(int32_t ss_idx)
{
  /*
   * Close filesystem
   */
  fs_close();

  /*
   * Unregister filesystem
   */
  fs_unregister();
}
