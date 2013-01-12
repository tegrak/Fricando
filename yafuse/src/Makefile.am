
MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

bin_PROGRAMS = yafuse

yafuse_LDADD = $(top_builddir)/libext4/libext4.la \
               $(top_builddir)/libfat32/libfat32.la

if REALLYSTATIC
yafuse_LDFLAGS = $(AM_LDFLAGS) -all-static
endif

yafuse_CFLAGS = $(AM_CFLAGS) \
	        -I$(top_srcdir)/include/libext4 \
	        -I$(top_srcdir)/include/libfat32

yafuse_SOURCES  = main.c

if RUN_LDCONFIG
install-exec-hook:
	$(LDCONFIG)
endif

