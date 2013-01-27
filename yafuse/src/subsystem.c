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
static int32_t ss_do_help(int32_t argc, char **argv);
static int32_t ss_do_history(int32_t argc, char **argv);
static int32_t ss_do_quit(int32_t argc, char **argv);

static void ss_add_history(const char *line);
static void ss_del_history();

static char* ss_completion_entry(const char *text, int32_t state);
static char** ss_attempted_completion(const char *text, int32_t start, int32_t end);

static fs_opt_handle_t ss_opt_hdl_match(const char *opt_cmd);
static void ss_exec_line(const char *line);
static void ss_listen(const char *ss_prompt, const char *fs_name);

/*
 * Global Variable Definition
 */
static int32_t fs_type;

static fs_opt_t ss_opt_tbl[SS_OPT_TBL_NUM_MAX] = {
  [0] = {
    .opt_hdl = ss_do_help,
    .opt_cmd = "help",
  },

  [1] = {
    .opt_hdl = ss_do_history,
    .opt_cmd = "history",
  },

  [2] = {
    .opt_hdl = ss_do_quit,
    .opt_cmd = "quit",
  },

  [3] = {
    .opt_hdl = NULL,
    .opt_cmd = NULL,
  }
};

static ss_data_t ss_data;

static const char* ss_history_buf[SS_HISTORY_BUF_LEN];
static int32_t ss_history_buf_idx;

/*
 * Function Definition
 */
static int32_t ss_do_help(int32_t argc, char **argv)
{
  int32_t opt_num = 0;
  const char *opt_cmd = NULL;
  int32_t i = 0;

  fprintf(stdout, "command list: ");

  for (i = 0; i < SS_OPT_TBL_NUM_MAX; ++i) {
    if (ss_opt_tbl[i].opt_hdl != NULL) {
      fprintf(stdout, "%s ", ss_opt_tbl[i].opt_cmd);
    } else {
      break;
    }
  }

  opt_num = fs_opt_num(fs_type);
  for (i = 0; i < opt_num; ++i) {
    opt_cmd = fs_opt_cmd_enum(fs_type, i);
    fprintf(stdout, "%s ", opt_cmd);
  }

  fprintf(stdout, "\n");

  return 0;
}

static int32_t ss_do_history(int32_t argc, char **argv)
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

static int32_t ss_do_quit(int32_t argc, char **argv)
{
  ss_data.abort = 1;

  return 0;
}

/*
 * Add subsystem command to command history
 */
static void ss_add_history(const char *line)
{
  char **ptr = NULL;
  int32_t len = 0, len_old = 0, len_new = 0;

  if (line == NULL || strlen(line) == 0) {
    return;
  }

  ss_history_buf_idx %= SS_HISTORY_BUF_LEN;
  ptr = (char **)&ss_history_buf[ss_history_buf_idx++];

  if (*ptr != NULL) {
    len_old = strlen(*ptr);
  } else {
    len_old = 0;
  }

  len_new = strlen(line);

  len = (len_old >= len_new) ? len_old : len_new;
  *ptr = (char *)realloc((void *)*ptr, (len + 1));
  if (*ptr != NULL) {
    memset((void *)*ptr, 0, (len + 1));
    strncpy(*ptr, line, len_new);
  }
}

/*
 * Delete history
 */
static void ss_del_history()
{
  int32_t i = 0;

  for (i = 0; i < SS_HISTORY_BUF_LEN; ++i) {
    if (ss_history_buf[i] != NULL) {
      free((void *)ss_history_buf[i]);
    }
  }
}

/*
 * Auto completion match entry
 */
static char* ss_completion_entry(const char *text, int32_t state)
{
  static int32_t ss_opt_tbl_idx;
  static int32_t len_txt = 0, len_cmd = 0;
  char *ptr = NULL;

  if (state == 0) {
    ss_opt_tbl_idx = 0;
    len_txt = strlen(text);
  }

  for (; ss_opt_tbl_idx < SS_OPT_TBL_NUM_MAX; ++ss_opt_tbl_idx) {
    if (ss_opt_tbl[ss_opt_tbl_idx].opt_cmd == NULL) {
      break;
    }

    len_cmd = strlen(ss_opt_tbl[ss_opt_tbl_idx].opt_cmd);

    if (len_cmd > 0 && len_cmd >= len_txt) {
      if (strncmp(ss_opt_tbl[ss_opt_tbl_idx].opt_cmd, text, len_txt) == 0) {
        ptr = (char *)malloc(len_cmd + 1);
        if (ptr != NULL) {
          memset((void *)ptr, 0, len_cmd + 1);
          strncpy(ptr, ss_opt_tbl[ss_opt_tbl_idx].opt_cmd, len_cmd);
          ++ss_opt_tbl_idx;
          break;
        }
      }
    }
  }

  return ptr;
}

/*
 * Auto completion callback
 */
static char** ss_attempted_completion(const char *text, int32_t start, int32_t end)
{
  char **match_list = NULL;

  if (start == 0) {
    match_list = rl_completion_matches((char *)text, &ss_completion_entry);
  } else {
    rl_bind_key('\t', rl_abort);
  }

  return match_list;
}

/*
 * Match opt handle with opt command
 */
static fs_opt_handle_t ss_opt_hdl_match(const char *ss_cmd)
{
  int32_t i = 0;
  int32_t len_ss_cmd = 0, len_opt_cmd = 0;
  fs_opt_handle_t handle = NULL;

  if (ss_cmd == NULL) {
    return ((fs_opt_handle_t)NULL);
  }

  len_ss_cmd = strlen(ss_cmd);

  for (i = 0; i < SS_OPT_TBL_NUM_MAX; ++i) {
    if (ss_opt_tbl[i].opt_cmd == NULL) {
      break;
    }

    len_opt_cmd = strlen(ss_opt_tbl[i].opt_cmd);

    if (len_opt_cmd > 0 && len_opt_cmd <= len_ss_cmd) {
      if (strncmp(ss_opt_tbl[i].opt_cmd, ss_cmd, len_opt_cmd) == 0) {
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
static void ss_exec_line(const char *line)
{
  fs_opt_handle_t handle = NULL;
  int32_t argc = 0;
  char *argv = NULL;
  int32_t ret = -1;

  argc = 1;
  argv = (char *)line;

  handle = fs_opt_hdl_match(fs_type, line);
  if (handle != NULL) {
    ret = handle(argc, (char **)&argv);
  } else {
    handle = ss_opt_hdl_match(line);
    if (handle != NULL) {
      ret = handle(argc, (char **)&argv);
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
  const char *line = NULL;

  /*
   * Open filesystem
   */
  if (fs_name != NULL) {
    fs_type = fs_open(fs_name);
  }

  /*
   * Init auto completion callback
   */
  rl_attempted_completion_function = ss_attempted_completion;

  /*
   * Read line
   */
  ss_data.abort = 0;

  while (ss_data.abort == 0) {
    /*
     * Init auto completion
     */
    rl_bind_key('\t', rl_complete);

    /*
     * Line processing
     */
    line = readline((const char *)ss_prompt);

    if (line != NULL && strlen(line) > 0) {
      ss_add_history(line);
      ss_exec_line(line);
    }

    if (line != NULL) {
      free((void *)line);
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

  if (ret_val == NULL) {
    fprintf(stderr, "ERROR: invalid args!\n");
    return -1;
  }

  /*
   * Display banner
   */
  fprintf(stdout, "WELCOME TO YAFUSE!\n");
  fprintf(stdout, "press 'help' for more info.\n");

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
   * Delete history
   */
  ss_del_history();

  /*
   * Close filesystem
   */
  fs_close();

  /*
   * Unregister filesystem
   */
  fs_unregister();
}
