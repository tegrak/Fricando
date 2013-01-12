#
# configure.ac - Source file to generate "./configure" to prepare package for
#		 compilation.
#
# Copyright (C) 2013-2014 angersax@gmail.com
#
# This program/include file is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program/include file is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (in the main directory of the YAFUSE
# distribution in the file COPYING); if not, write to the Free Software
# Foundation,Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Autoconf
AC_PREREQ(2.59)
AC_INIT([yafuse],[2013.1.12],[angersax@gmail.com])
YAFUSE_VERSION="1"
LIBEXT4_VERSION="1"
LIBFAT32_VERSION="1"
AC_CONFIG_SRCDIR([src/main.c])

# Environment
AC_CANONICAL_HOST
AC_CANONICAL_TARGET

# Automake
AM_INIT_AUTOMAKE([${PACKAGE_NAME}], [${PACKAGE_VERSION}])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_MACRO_DIR([m4])
AM_MAINTAINER_MODE

# Options
AC_ARG_ENABLE(
	[debug],
	[AS_HELP_STRING([--enable-debug],[enable debugging code and output])],
	,
	[enable_debug="no"]
)

AC_ARG_ENABLE(
	[really-static],
	[AS_HELP_STRING([--enable-really-static],[create fully static binaries])],
	,
	[enable_really_static="no"]
)

AC_ARG_ENABLE(
	[library],
	[AS_HELP_STRING([--disable-library],[do not install library but link it into yafuse])],
	,
	[enable_library="yes"]
)

# Programs
AC_PROG_CC(gcc cc)
AC_PROG_LN_S
AM_PROG_CC_C_O

ifdef(
	[LT_INIT],
	[LT_INIT],
	[AC_PROG_LIBTOOL]
)

AC_PROG_INSTALL
PKG_PROG_PKG_CONFIG

AC_PATH_PROG([MV], [mv])
AC_PATH_PROG([RM], [rm])
AC_PATH_PROG([SED], [sed])
AC_ARG_VAR([LDCONFIG], [ldconfig utility])
AC_PATH_PROG([LDCONFIG], [ldconfig], [true], [/sbin /usr/sbin $PATH])

# Environment
AC_MSG_CHECKING([Windows OS])
case "${target}" in
*-mingw32*|*-winnt*|*-cygwin*)
	AC_MSG_RESULT([yes])
	WINDOWS="yes"
	AC_DEFINE(
		[WINDOWS],
		[1],
		[Define to 1 if this is a Windows OS]
	)
	;;
*)
	AC_MSG_RESULT([no])
	WINDOWS="no"
	;;
esac

if test "${enable_ldscript}" = "yes"; then
        AC_MSG_CHECKING([Output format])
        OUTPUT_FORMAT="$(${CC} ${CFLAGS} ${LDFLAGS} -Wl,--verbose 2>&1 | ${SED} -n 's/^OUTPUT_FORMAT("\([[^"]]*\)",.*/\1/p')"
        if test -z "${OUTPUT_FORMAT}"; then
                AC_MSG_RESULT([None])
        else
                AC_MSG_RESULT([${OUTPUT_FORMAT}])
                OUTPUT_FORMAT="OUTPUT_FORMAT ( ${OUTPUT_FORMAT} )"
        fi
fi

# Checks for header files.
AC_HEADER_STDC
AC_CHECK_HEADERS([stddef.h stdint.h stdlib.h stdio.h stdarg.h string.h \
	          strings.h errno.h time.h unistd.h utime.h wchar.h getopt.h features.h \
	          endian.h byteswap.h windows.h syslog.h pwd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_HEADER_STDBOOL
AC_C_BIGENDIAN(
	,
	[
		AC_DEFINE(
			[WORDS_LITTLEENDIAN],
			[1],
			[Define to 1 if your processor stores words with the least significant
			byte first (like Intel and VAX, unlike Motorola and SPARC).]
		)
	]
	,
)
AC_C_CONST
AC_C_INLINE
AC_TYPE_OFF_T
AC_TYPE_SIZE_T
AC_STRUCT_ST_BLOCKS
AC_CHECK_MEMBERS([struct stat.st_rdev])
AC_CHECK_MEMBERS([struct stat.st_atim])
AC_CHECK_MEMBERS([struct stat.st_atimespec])
AC_CHECK_MEMBERS([struct stat.st_atimensec])

# Checks for library functions.
AC_FUNC_GETMNTENT
AC_FUNC_MBRTOWC
AC_FUNC_MEMCMP
AC_FUNC_STAT
AC_FUNC_STRFTIME
AC_FUNC_UTIME_NULL
AC_FUNC_VPRINTF
AC_CHECK_FUNCS([atexit basename daemon dup2 fdatasync ffs getopt_long hasmntopt \
	        mbsinit memmove memset realpath regcomp setlocale setxattr \
	        strcasecmp strchr strdup strerror strnlen strsep strtol strtoul \
	        sysconf utime utimensat gettimeofday clock_gettime fork])
AC_SYS_LARGEFILE

if test "$GCC" = "yes" ; then
	# We add -Wall to enable some compiler warnings.
	CFLAGS="${CFLAGS} -Wall"
fi

if test "${enable_warnings}" = "yes"; then
	CFLAGS="${CFLAGS} -W -Wall -Waggregate-return -Wbad-function-cast -Wcast-align -Wcast-qual -Wdisabled-optimization -Wdiv-by-zero -Wfloat-equal -Winline -Wmissing-declarations -Wmissing-format-attribute -Wmissing-noreturn -Wmissing-prototypes -Wmultichar -Wnested-externs -Wpointer-arith -Wredundant-decls -Wshadow -Wsign-compare -Wstrict-prototypes -Wundef -Wwrite-strings -Wformat -Wformat-security -Wuninitialized"
fi

if test "${enable_debug}" = "yes"; then
	CFLAGS="${CFLAGS} -ggdb3 -DDEBUG"
	AC_DEFINE(
		[ENABLE_DEBUG],
		[1],
		[Define to 1 if debug should be enabled]
	)
fi

test "${enable_really_static}" = "yes" && enable_library="no"

# Settings
pkgconfigdir="\$(libdir)/pkgconfig"
libext4includedir="\$(includedir)/libext4"
libfat32includedir="\$(includedir)/libfat32"
AC_SUBST([pkgconfigdir])
AC_SUBST([libext4includedir])
AC_SUBST([libfat32includedir])
AC_SUBST([YAFUSE_VERSION])
AC_SUBST([LIBEXT4_VERSION])
AC_SUBST([LIBFAT32_VERSION])
AM_CONDITIONAL([GENERATE_LDSCRIPT], [test "${enable_ldscript}" = "yes"])
AM_CONDITIONAL([WINDOWS], [test "${WINDOWS}" = "yes"])
AM_CONDITIONAL([RUN_LDCONFIG], [test "${enable_ldconfig}" = "yes"])
AM_CONDITIONAL([REALLYSTATIC], [test "${enable_really_static}" = "yes"])
AM_CONDITIONAL([INSTALL_LIBRARY], [test "${enable_library}" = "yes"])

# generate files
AC_CONFIG_FILES([
	Makefile
	include/Makefile
	include/libext4/Makefile
	include/libfat32/Makefile
	libext4/Makefile
	libfat32/Makefile
	src/Makefile])
AC_OUTPUT

echo "You can type now 'make' to build yafuse."

