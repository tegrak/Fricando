/**
 * main.c - Main entry of YAFUSE.
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
#ifdef HAVE_FCNTL_H
#include <fcntl.h>
#endif
#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif
#ifdef HAVE_STDLIB_H
#include <stdlib.h>
#endif
#ifdef HAVE_LOCALE_H
#include <locale.h>
#endif
#ifdef HAVE_LIMITS_H
#include <limits.h>
#endif
#ifdef HAVE_STDINT_H
#include <stdint.h>
#endif
#ifdef HAVE_GETOPT_H
#include <getopt.h>
#endif

#ifdef DEBUG
// Add code here
#endif

#include "filesystem.h"
#include "fs_ext4.h"
#include "fs_fat32.h"
#include "subsystem.h"
#include "include/debug.h"

/*
 * Macro Definition
 */
/* Option string */
#define OPTION_STR  "hVv"

/* Subsystem name */
#define SS_NAME  "yafuse"

/*
 * Type Definition
 */

/*
 * Global Variable Definition
 */

/*
 * Function Declaration
 */
static void print_usage();

/*
 * Function Definition
 */
/*
 * Print usage
 */
static void print_usage()
{
  fprintf(stdout, "\n");
  fprintf(stdout, "Usage:  yafuse [option] <device|image_file>\n");
  fprintf(stdout, "\n");
  fprintf(stdout, "Options:\n");
  fprintf(stdout, "  -h    print this help, then exit\n");
  fprintf(stdout, "  -V    print version number, then exit\n");
  fprintf(stdout, "  -v    verbosely report processing\n");
  fprintf(stdout, "\n");
  fprintf(stdout, "Example:\n");
  fprintf(stdout, "  yafuse -v sample.ext4\n");
  fprintf(stdout, "\n");
}

int32_t main(int argc, char *argv[])
{
  int32_t c = 0;
  int32_t verbose = 0;
  const char *fs_name = NULL;
  int32_t ss_idx = 0;
  int32_t ret = 0;

  /*
   * Parse options
   */
  while ((c = getopt(argc, argv, OPTION_STR)) != EOF) {
    switch (c) {
    case 'V':
      fprintf(stdout, "yafuse 1.0\n");
      exit(0);
    case 'v':
      verbose = 1;
      break;
    default:
      print_usage();
      return 1;
    }
  }

  /*
   * Register filesystem
   */
  ret = fs_register(fs_opt_tbl_ext4);
  if (ret != 0) {
    error("failed to register ext4 operation table!");
    return -1;
  }

  ret = fs_register(fs_opt_tbl_fat32);
  if (ret != 0) {
    error("failed to register fat32 operation table!");
    return -1;
  }

  /*
   * Create subsystem
   */
  if (optind < argc) {
    fs_name = argv[optind];
  } else {
    fs_name = NULL;
  }

  ss_idx = ss_create(SS_NAME, fs_name, &ret);
  if (ret != 0) {
    error("failed to create subsystem!");
    return ret;
  }

  ss_delete(ss_idx);

  return 0;
}
