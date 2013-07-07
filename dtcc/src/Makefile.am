#
# Add subdirectories
#
SUBDIRS = libfdt

#
# Build dtcc
#
bin_PROGRAMS = dtcc

dtcc_LDADD = $(top_builddir)/src/libfdt/libfdt.la

if REALLYSTATIC
dtcc_LDFLAGS = $(AM_LDFLAGS) -all-static
endif

dtcc_CFLAGS = $(AM_CFLAGS) \
              -I$(top_srcdir)/src/libfdt \
              -I$(top_srcdir)/src

dtcc_SOURCES = dtc-parser.tab.c \
               dtc-lexer.lex.c \
               checks.c \
               data.c \
               flattree.c \
               fstree.c \
               livetree.c \
               srcpos.c \
               treesource.c \
               util.c \
               dtc.c

if RUN_LDCONFIG
install-exec-hook:
	$(LDCONFIG)
endif

clean-local:
	@rm -f $(bin_PROGRAMS)

##
## Build fdtdump
##
#bin_PROGRAMS = fdtdump
#
#fdtdump_LDADD = $(top_builddir)/src/libfdt/libfdt.la
#
#if REALLYSTATIC
#fdtdump_LDFLAGS = $(AM_LDFLAGS) -all-static
#endif
#
#fdtdump_CFLAGS = $(AM_CFLAGS) \
#                 -I$(top_srcdir)/src/libfdt \
#                 -I$(top_srcdir)/src
#
#fdtdump_SOURCES  = fdtdump.c
#
##
## Build fdtget
##
#bin_PROGRAMS = fdtget
#
#fdtget_LDADD = $(top_builddir)/src/libfdt/libfdt.la
#
#if REALLYSTATIC
#fdtget_LDFLAGS = $(AM_LDFLAGS) -all-static
#endif
#
#fdtget_CFLAGS = $(AM_CFLAGS) \
#                -I$(top_srcdir)/src/libfdt \
#                -I$(top_srcdir)/src
#
#fdtget_SOURCES  = fdtget.c
#
##
## Build fdtput
##
#bin_PROGRAMS = fdtput
#
#fdtput_LDADD = $(top_builddir)/src/libfdt/libfdt.la
#
#if REALLYSTATIC
#fdtput_LDFLAGS = $(AM_LDFLAGS) -all-static
#endif
#
#fdtput_CFLAGS = $(AM_CFLAGS) \
#                -I$(top_srcdir)/src/libfdt \
#                -I$(top_srcdir)/src
#
#fdtput_SOURCES  = fdtput.c

