
MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

SUBDIRS = libext4 libfat32 libio

headers = debug.h \
          types.h

if INSTALL_LIBRARY
include_HEADERS = $(headers)
else
noinst_HEADERS = $(headers)
endif
