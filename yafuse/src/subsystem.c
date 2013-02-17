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

#include "include/debug.h"

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
static int32_t ss_do_help(int32_t argc, const char **argv);
static int32_t ss_do_history(int32_t argc, const char **argv);
static int32_t ss_do_quit(int32_t argc, const char **argv);

static void ss_add_history(const char *line);
static void ss_del_history(void);

static inline char* ss_completion_entry_helper(const char *cmd, int32_t len_cmd, const char *text, int32_t len_txt);
static char* ss_completion_entry(const char *text, int32_t state);
static char** ss_attempted_completion(const char *text, int32_t start, int32_t end);

static fs_opt_handle_t ss_opt_hdl_match(const char *opt_cmd);
static int32_t ss_parse_line(char *line, int32_t *argc, const char **argv);
static void ss_exec_line(char *line);
static void ss_listen(const char *ss_prompt, const char *fs_name);

/*
 * Global Variable Definition
 */
static int32_t fs_type = -1;

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

static char* ss_history_buf[SS_HISTORY_BUF_LEN];
static int32_t ss_history_buf_idx;

/*
 * Function Definition
 */
static int32_t ss_do_help(int32_t argc, const char **argv)
{
  int32_t opt_num = 0;
  const char *opt_cmd = NULL;
  int32_t i = 0;

  argc = argc;
  argv =argv;

  fprintf(stdout, "command list: ");

  for (i = 0; i < SS_OPT_TBL_NUM_MAX; ++i) {
    if (ss_opt_tbl[i].opt_hdl != NULL) {
      fprintf(stdout, "%s ", ss_opt_tbl[i].opt_cmd);
    } else {
      break;
    }
  }

  opt_num = fs_opt_num(fs_type);
  if (opt_num > 0) {
    for (i = 0; i < opt_num; ++i) {
      opt_cmd = fs_opt_cmd_enum(fs_type, i);
      fprintf(stdout, "%s ", opt_cmd);
    }
  } else {
    fprintf(stdout, "%s %s", FS_OPT_CMD_MOUNT, FS_OPT_CMD_UMOUNT);
  }

  fprintf(stdout, "\n");

  return 0;
}

static int32_t ss_do_history(int32_t argc, const char **argv)
{
  int32_t idx = 0;
  int32_t i = 0, j = 0;

  argc = argc;
  argv = argv;

  idx = ss_history_buf_idx % SS_HISTORY_BUF_LEN;

  for (i = 0, j = 0; i < SS_HISTORY_BUF_LEN; ++i, ++idx) {
    idx %= SS_HISTORY_BUF_LEN;
    if (ss_history_buf[idx] != NULL) {
      fprintf(stdout, "%d  %s\n", j++, ss_history_buf[idx]);
    }
  }

  return 0;
}

static int32_t ss_do_quit(int32_t argc, const char **argv)
{
  argc = argc;
  argv = argv;

  ss_data.abort = 1;

  return 0;
}

/*
 * Add subsystem command to command history
 */
static void ss_add_history(const char *line)
{
  char **cmd = NULL;
  size_t len = 0, len_old = 0, len_new = 0;

  if (line == NULL || strlen(line) == 0) {
    return;
  }

  ss_history_buf_idx %= SS_HISTORY_BUF_LEN;
  cmd = (char **)&ss_history_buf[ss_history_buf_idx++];

  if (*cmd != NULL) {
    len_old = strlen(*cmd);
  } else {
    len_old = 0;
  }

  len_new = strlen(line);

  len = (len_old >= len_new) ? len_old : len_new;
  *cmd = (char *)realloc((void *)*cmd, (len + 1));
  if (*cmd != NULL) {
    memset((void *)*cmd, 0, (len + 1));
    strncpy(*cmd, line, len_new);
  }
}

/*
 * Delete history
 */
static void ss_del_history(void)
{
  int32_t i = 0;

  for (i = 0; i < SS_HISTORY_BUF_LEN; ++i) {
    if (ss_history_buf[i] != NULL) {
      free((void *)ss_history_buf[i]);
      ss_history_buf[i] = NULL;
    }
  }
}

static inline char* ss_completion_entry_helper(const char *cmd, int32_t len_cmd, const char *text, int32_t len_txt)
{
  static char *match = NULL;

  if (strncmp(cmd, text, len_txt) == 0) {
    match = (char *)malloc(len_cmd + 1);
    if (match != NULL) {
      memset((void *)match, 0, len_cmd + 1);
      strncpy(match, cmd, len_cmd);
      return match;
    }
  }

  return ((char *)NULL);
}

/*
 * Auto completion match entry
 */
static char* ss_completion_entry(const char *text, int32_t state)
{
  static int32_t ss_opt_tbl_idx = 0, fs_opt_tbl_idx = 0;
  static int32_t fs_opt_tbl_num = 0;
  static int32_t mnt_opt_num = 0;
  static size_t len_txt = 0, len_cmd = 0;
  static const char *cmd = NULL;
  static char *match = NULL;

  if (state == 0) {
    ss_opt_tbl_idx = 0;
    fs_opt_tbl_idx = 0;
    fs_opt_tbl_num = fs_opt_num(fs_type);
    mnt_opt_num = 0;
    len_txt = strlen(text);
  }

  for (; ss_opt_tbl_idx < SS_OPT_TBL_NUM_MAX; ++ss_opt_tbl_idx) {
    if (ss_opt_tbl[ss_opt_tbl_idx].opt_cmd == NULL) {
      break;
    }
    len_cmd = strlen(ss_opt_tbl[ss_opt_tbl_idx].opt_cmd);
    if (len_cmd > 0 && len_cmd >= len_txt) {
      match = ss_completion_entry_helper(ss_opt_tbl[ss_opt_tbl_idx].opt_cmd, len_cmd, text, len_txt);
      if (match != NULL) {
        ++ss_opt_tbl_idx;
        return match;
      }
    }
  }

  if (fs_opt_tbl_num > 0) {
    for (; fs_opt_tbl_idx < fs_opt_tbl_num; ++fs_opt_tbl_idx) {
      cmd = fs_opt_cmd_enum(fs_type, fs_opt_tbl_idx);
      if (cmd == NULL) {
        break;
      }
      len_cmd = strlen(cmd);
      if (len_cmd > 0 && len_cmd >= len_txt) {
        match = ss_completion_entry_helper(cmd, len_cmd, text, len_txt);
        if (match != NULL) {
          ++fs_opt_tbl_idx;
          return match;
        }
      }
    }
  } else {
    if (mnt_opt_num == 0) {
      if (strlen(FS_OPT_CMD_MOUNT) >= len_txt) {
        match = ss_completion_entry_helper(FS_OPT_CMD_MOUNT, strlen(FS_OPT_CMD_MOUNT), text, len_txt);
        if (match != NULL) {
          ++mnt_opt_num;
          return match;
        } else {
          if (strlen(FS_OPT_CMD_UMOUNT) >= len_txt) {
            match = ss_completion_entry_helper(FS_OPT_CMD_UMOUNT, strlen(FS_OPT_CMD_UMOUNT), text, len_txt);
            if (match != NULL) {
              ++mnt_opt_num;
              return match;
            }
          }
        }
      }
    }
  }

  return ((char *)NULL);
}

/*
 * Auto completion callback
 */
static char** ss_attempted_completion(const char *text, int32_t start, int32_t end)
{
  char **match_list = NULL;

  end = end;

  if (start == 0) {
    match_list = rl_completion_matches(text, &ss_completion_entry);
  }

  return match_list;
}

/*
 * Match opt handle with opt command
 */
static fs_opt_handle_t ss_opt_hdl_match(const char *ss_cmd)
{
  int32_t i = 0;
  size_t len_ss_cmd = 0, len_opt_cmd = 0;
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
 * Parse command line
 */
static int32_t ss_parse_line(char *line, int32_t *argc, const char **argv)
{
  char *buf = NULL, *ptr = NULL;
  int32_t count = 0;

  if (line == NULL || argc == NULL || argv == NULL) {
    error("invalid args!");
    return -1;
  }

  buf = line;

  while ((ptr = strtok(buf, FS_OPT_CMD_ARG_DELIM)) != NULL) {
    if ((++count) > FS_OPT_CMD_ARG_NUM_MAX) {
      error("invalid args!");
      return -1;
    }
    argv[count - 1] = ptr;
    buf = NULL;
  }

  *argc = count;

  return 0;
}

/*
 * Execute command line for filesystem
 */
static void ss_exec_line(char *line)
{
  fs_opt_handle_t handle = NULL;
  int32_t argc = 0;
  const char* argv[FS_OPT_CMD_ARG_NUM_MAX] = {NULL};
  int32_t len_s1 = 0, len_s2 = 0;
  int32_t ret = -1;

  ret = ss_parse_line(line, &argc, argv);
  if (ret != 0) {
    fprintf(stdout, "press 'help' for more info.\n");
    return;
  }

  handle = ss_opt_hdl_match(argv[0]);
  if (handle != NULL) {
    ret = handle(argc, argv);
    if (ret != 0) {
      goto ss_exec_line_fail;
    }
    return;
  }

  len_s1 = strlen(argv[0]);
  len_s2 = strlen(FS_OPT_CMD_MOUNT);

  if (len_s1 == len_s2) {
    if (strncmp(argv[0], FS_OPT_CMD_MOUNT, len_s1) == 0) {
      fs_type = fs_mount(argv[1]);
      return;
    }
  }

  if (fs_type < 0) {
   return;
  }

  len_s1 = strlen(argv[0]);
  len_s2 = strlen(FS_OPT_CMD_UMOUNT);

  if (len_s1 == len_s2) {
    if (strncmp(argv[0], FS_OPT_CMD_UMOUNT, len_s1) == 0) {
      fs_umount(fs_type);
      fs_type = -1;
      return;
    }
  }

  handle = fs_opt_hdl_match(fs_type, (const char *)argv[0]);
  if (handle != NULL) {
    ret = handle(argc, argv);
  }

  return;

ss_exec_line_fail:
  fprintf(stdout, "press 'help' for more info.\n");
  return;
}

/*
 * Listen for reading line in subsystem
 */
static void ss_listen(const char *ss_prompt, const char *fs_name)
{
  char *line = NULL;

  /*
   * Mount filesystem
   */
  if (fs_name != NULL) {
    fs_type = fs_mount(fs_name);
  } else {
    fs_type = -1;
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
      line = NULL;
    }
  }
}

/*
 * Create subsystem
 */
int32_t ss_create(const char *ss_name, const char *fs_name, int32_t *ret_val)
{
  char ss_prompt[SS_NAME_LEN_MAX + SS_PROMPT_DEFAULT_LEN + 1] = {0};
  size_t ss_prompt_len = 0;

  if (ret_val == NULL) {
    error("invalid args!");
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
  ss_idx = ss_idx;

  /*
   * Delete history
   */
  ss_del_history();

  /*
   * Umount filesystem
   */
  fs_umount(fs_type);
  fs_type = -1;

  /*
   * Unregister filesystem
   */
  fs_unregister();
}
