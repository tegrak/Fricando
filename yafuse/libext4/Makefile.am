
MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

if INSTALL_LIBRARY
lib_LTLIBRARIES    = libext4.la
pkgconfig_DATA     = libext4.pc
else
noinst_LTLIBRARIES = libext4.la
endif

libext4_la_CFLAGS  = $(AM_CFLAGS) -I$(top_srcdir)/include/libext4

libext4_la_LDFLAGS = -version-info $(LIBEXT4_VERSION) -no-undefined

libext4_la_SOURCES = super.c

if WINDOWS
libext4_la_SOURCES += bio.c
else
libext4_la_SOURCES += bio.c
endif

