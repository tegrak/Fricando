MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

if INSTALL_LIBRARY
lib_LTLIBRARIES    = libfdt.la
pkgconfig_DATA     = libfdt.pc
else
noinst_LTLIBRARIES = libfdt.la
endif

libfdt_la_CFLAGS  = $(AM_CFLAGS)

libfdt_la_SOURCES = fdt.c \
                    fdt_empty_tree.c \
                    fdt_ro.c \
                    fdt_rw.c \
                    fdt_strerror.c \
                    fdt_sw.c \
                    fdt_wip.c

if WINDOWS
libfdt_la_SOURCES +=
else
libfdt_la_SOURCES +=
endif

clean-local:
	@rm -f $(lib_LTLIBRARIES)

