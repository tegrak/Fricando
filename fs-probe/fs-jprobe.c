/**
 * fs-jprobe.c - jprobe for linux kernel file system.
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
 * along with this program (in the main directory of the distribution
 * in the file COPYING); if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/kprobes.h>
#include <linux/kallsyms.h>
#include <linux/fs.h>

/*
 * Macro Definition
 */

/*
 * Type Definition
 */
enum {
  JP_OPEN = 0,
  JP_MAX  = 1
};

struct open_flags {
  int32_t open_flag;
  umode_t mode;
  int32_t acc_mode;
  int32_t intent;
};

/*
 * Function Declaration
 */
static struct file* jp_do_filp_open(int32_t dfd, const char *pathname, const struct open_flags *op, int32_t flags);

/*
 * Global Variable Definition
 */
static struct jprobe jp_open = {
  .kp = {
    .symbol_name = "do_filp_open",
  },
  .entry = jp_do_filp_open
};

static struct jprobe* fs_jp[] = {
  [JP_OPEN] = &jp_open,
};

static int32_t fs_jp_num = sizeof(fs_jp) / sizeof(fs_jp[0]);

/*
 * Function Definition
 */
static struct file* jp_do_filp_open(int32_t dfd, const char *pathname, const struct open_flags *op, int32_t flags)
{
  pr_info("%s: pid: %d, pathname: %s, open_flag: %d, mode: %d, acc_mode: %d, intent: %d, flags: %d\n",
          __func__, current->pid, pathname, op->open_flag, op->mode, op->acc_mode, op->intent, flags);
  jprobe_return();
  return 0;
}

static int32_t __init jprobe_init(void)
{
  int32_t i = 0;
  int32_t ret = 0;

  ret = register_jprobes(fs_jp, fs_jp_num);
  if (ret < 0) {
    pr_err("%s: failed to register_jprobe: %d!\n", __func__, ret);
    return ret;
  }

  for (i = 0; i < fs_jp_num; ++i) {
    pr_info("%s: symbol: %s, planted at %p, handler addr %p\n", __func__, fs_jp[i]->kp.symbol_name, fs_jp[i]->kp.addr, fs_jp[i]->entry);
  }

  return 0;
}

static void __exit jprobe_exit(void)
{
  int32_t i = 0;

  unregister_jprobes(fs_jp, fs_jp_num);

  for (i = 0; i < fs_jp_num; ++i) {
    pr_info("%s: symbol: %s, unregistered at %p\n", __func__, fs_jp[i]->kp.symbol_name, fs_jp[i]->kp.addr);
  }
}

module_init(jprobe_init)
module_exit(jprobe_exit)
MODULE_LICENSE("GPL");
