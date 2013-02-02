
MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

if INSTALL_LIBRARY
lib_LTLIBRARIES    = libio.la
pkgconfig_DATA     = libio.pc
else
noinst_LTLIBRARIES = libio.la
endif

libio_la_CFLAGS  = $(AM_CFLAGS) -I$(top_srcdir)/include -I$(top_srcdir)/include/libio

libio_la_LDFLAGS = -version-info $(LIBIO_VERSION) -no-undefined

libio_la_SOURCES = io.c

if WINDOWS
libio_la_SOURCES +=
else
libio_la_SOURCES +=
endif
