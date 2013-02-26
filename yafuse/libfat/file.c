/**
 * file.c - file of FAT.
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

/*
 * Macro Definition
 */

/*
 * Type Definition
 */

/*
 * Global Variable Definition
 */

/*
 * Function Declaration
 */

/*
 * Function Definition
 */
int32_t fat_fill_file(const struct fat_super_block *sb, int32_t cluster, size_t size, uint8_t *buf)
{
  int32_t sector = 0;
  int32_t offset = 0;
  int32_t ret = 0;

  ret = fat_fill_clus2sec(sb, cluster, &sector);
  if (ret != 0) {
    return -1;
  }

  offset = sector * (int32_t)GET_UNALIGNED_LE16(sb->bs.sector_size);

  ret = io_fseek(offset);
  if (ret != 0) {
    return -1;
  }

  ret = io_fread(buf, size);
  if (ret != 0) {
    return -1;
  }

  return 0;
}
