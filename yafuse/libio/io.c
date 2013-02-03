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
 * along with this program (in the main directory of the NTFS-3G
 * distribution in the file COPYING); if not, write to the Free Software
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
#define O_BINARY  (0)

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
static int32_t io_fseek(int32_t fd, int32_t offset);
static int32_t io_fread(int32_t fd, uint8_t *data, int32_t len);
static int32_t io_fwrite(int32_t fd, uint8_t *data, int32_t len);

/*
 * Function Definition
 */
static int32_t io_fopen(const char *fs_name)
{
  return open(fs_name, O_WRONLY | O_BINARY);
}

static void io_fclose(int32_t fd)
{
  close(fd);
}

static int32_t io_fseek(int32_t fd, int32_t offset)
{
  return lseek(fd, offset, SEEK_SET);
}

static int32_t io_fread(int32_t fd, uint8_t *data, int32_t len)
{
  return read(fd, (void *)data, len);
}

static int32_t io_fwrite(int32_t fd, uint8_t *data, int32_t len)
{
  return write(fd, (void *)data, len);
}

/*
 * Open IO
 */
int32_t io_open(const char *fs_name)
{
  if (fs_name == NULL) {
    error("invalid args!");
    return -1;
  }

  if (io_fd >= 0) {
    info("close io first.");
    return -1;
  }

  io_fd = io_fopen(fs_name);
  if (io_fd < 0) {
    error("failed to open io!");
    return -1;
  }

  return 0;
}

/*
 * Close IO
 */
void io_close()
{
  if (io_fd < 0) {
    return;
  }

  io_fclose(io_fd);

  io_fd = -1;
}

/*
 * Seek IO
 */
int32_t io_seek(int32_t offset)
{
  int32_t ret = 0;

  if (io_fd < 0 || offset < 0) {
    error("invalid args!");
    return -1;
  }    

  ret = io_fseek(io_fd, offset);
  if (ret < 0) {
    error("failed to seek io!");
    return -1;
  }

  return 0;
}

/*
 * Read IO
 */
int32_t io_read(uint8_t *data, int32_t len)
{
  int32_t ret = 0;

  if (io_fd < 0 || data == NULL || len <= 0) {
    error("invalid args!");
    return -1;
  }    

  ret = io_fread(io_fd, data, len);
  if (ret < 0) {
    error("failed to read io!");
    return -1;
  } else if (ret < len) {
    error("failed to read io completely!");
    return -1;
  }

  return 0;
}

/*
 * Write IO
 */
int32_t io_write(uint8_t *data, int32_t len)
{
  int32_t ret = 0;

  if (io_fd < 0 || data == NULL || len <= 0) {
    error("invalid args!");
    return -1;
  }

  ret = io_fwrite(io_fd, data, len);
  if (ret < 0) {
    error("failed to write io!");
    return -1;
  } else if (ret < len) {
    error("failed to write io completely!");
    return -1;
  }

  return 0;
}
