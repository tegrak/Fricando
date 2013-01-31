
MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

if INSTALL_LIBRARY
lib_LTLIBRARIES    = libfat32.la
pkgconfig_DATA     = libfat32.pc
else
noinst_LTLIBRARIES = libfat32.la
endif

libfat32_la_CFLAGS  = $(AM_CFLAGS) -I$(top_srcdir)/include/libfat32 -I$(top_srcdir)/include/libio

libfat32_la_LDFLAGS = -version-info $(LIBFAT32_VERSION) -no-undefined

libfat32_la_SOURCES = super.c

if WINDOWS
libfat32_la_SOURCES +=
else
libfat32_la_SOURCES +=
endif

