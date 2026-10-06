/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_FILESYSTEM_H
#define OPENCFW_BOOT_FILESYSTEM_H
#include "upstream/lfs.h"
extern const struct lfs_config opencfw_boot_lfs_config;
int opencfw_boot_lfs_read(const struct lfs_config *,lfs_block_t,lfs_off_t,void *,lfs_size_t);
int opencfw_boot_lfs_prog(const struct lfs_config *,lfs_block_t,lfs_off_t,const void *,lfs_size_t);
int opencfw_boot_lfs_erase(const struct lfs_config *,lfs_block_t);
int opencfw_boot_lfs_sync(const struct lfs_config *);
/* Platform dependencies. Recovered callback semantics, not implementations. */
uint32_t opencfw_boot_nor_read(uint32_t,void *,uint32_t);
uint32_t opencfw_boot_nor_prog(uint32_t,const void *,uint32_t);
uint32_t opencfw_boot_nor_erase(uint32_t);
void opencfw_boot_fs_error(uintptr_t format,...);
#endif
