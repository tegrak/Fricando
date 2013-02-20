/**
 * io.c - IO interface for filesystem.
 *
 * Copyright (c) 2013-2014 angersax@gmail.com
 *
 * This program/include file is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as published
 * by the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program/include file is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty
 * of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program (in the main directory of the distribution
 * in the file COPYING); if not, write to the Free Software
 * Foundation,Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
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
#include "include/libio/io.h"

/*
 * Macro Definition
 */
#ifndef O_BINARY
#define O_BINARY  (0)
#endif

/*
 * Type Definition
 */

/*
 * Global Variable Definition
 */
static int32_t io_fd = -1;

/*
 * Function Declaration
 */
static int32_t io_fopen(const char *fs_name);
static void io_fclose(int32_t fd);

/*
 * Function Definition
 */
static int32_t io_fopen(const char *fs_name)
{
  const char *name = NULL;
  int32_t ret = 0;

  name = fs_name;

  ret = access(name, F_OK);
  if (ret != 0) {
    return -1;
  }

  ret = access(name, R_OK | W_OK);
  if (ret != 0) {
    return -1;
  }

  return open(name, O_RDWR | O_BINARY);
}

static void io_fclose(int32_t fd)
{
  close(fd);
}

/*
 * Open IO
 */
int32_t io_open(const char *fs_name)
{
  if (fs_name == NULL) {
    return -1;
  }

  if (io_fd >= 0) {
    error("close io first.");
    return -1;
  }

  io_fd = io_fopen(fs_name);
  if (io_fd < 0) {
    return -1;
  }

  return 0;
}

/*
 * Close IO
 */
void io_close(void)
{
  if (io_fd < 0) {
    return;
  }

  io_fclose(io_fd);

  io_fd = -1;
}

/*
 * Seek IO of file
 */
int32_t io_fseek(off_t offset)
{
  int32_t ret = 0;

  if (offset < 0) {
    return -1;
  }    

  if (io_fd < 0) {
    error("invalid args!");
    return -1;
  }    

  ret = lseek(io_fd, offset, SEEK_SET);
  if (ret < 0) {
    return -1;
  }

  return 0;
}

/*
 * Read IO of file
 */
int32_t io_fread(uint8_t *data, size_t len)
{
  ssize_t ret = 0;

  if (data == NULL || len <= 0) {
    return -1;
  }    

  if (io_fd < 0) {
    error("invalid args!");
    return -1;
  }    

  ret = read(io_fd, (void *)data, len);
  if (ret < 0) {
    return -1;
  }

  return 0;
}

/*
 * Write IO of file
 */
int32_t io_fwrite(uint8_t *data, size_t len)
{
  ssize_t ret = 0;

  if (data == NULL || len <= 0) {
    return -1;
  }

  if (io_fd < 0) {
    error("invalid args!");
    return -1;
  }

  ret = write(io_fd, (const void *)data, len);
  if (ret < 0) {
    return -1;
  }

  return 0;
}

/*
 * Seek IO of block
 */
int32_t io_bseek(size_t count, size_t bs)
{
  // Add code here
  count = count;
  bs = bs;

  return -1;
}

/*
 * Read IO of block
 */
int32_t io_bread(uint8_t *data, size_t count, size_t bs)
{
  // Add code here
  data = data;
  count = count;
  bs = bs;

  return -1;
}

/*
 * Write IO of block
 */
int32_t io_bwrite(uint8_t *data, size_t count, size_t bs)
{
  // Add code here
  data = data;
  count = count;
  bs = bs;

  return -1;
}
