/**
 * io.h - The header of IO interface.
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

#ifndef _IO_H
#define _IO_H

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef HAVE_STDINT_H
#include <stdint.h>
#endif

#ifdef DEBUG
// Add code here
#endif

#include "include/types.h"

/*
 * Macro Definition
 */

/*
 * Type Definition
 */

/*
 * Function Declaration
 */
int32_t io_open(const char *fs_name);
void io_close(void);

int32_t io_fseek(off_t offset);
int32_t io_fread(uint8_t *data, size_t len);
int32_t io_fwrite(uint8_t *data, size_t len);

int32_t io_bseek(size_t count, size_t bs);
int32_t io_bread(uint8_t *data, size_t count, size_t bs);
int32_t io_bwrite(uint8_t *data, size_t count, size_t bs);

#endif /* _IO_H */
