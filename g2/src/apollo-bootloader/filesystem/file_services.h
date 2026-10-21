/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_FILE_SERVICES_H
#define OPENCFW_BOOT_FILE_SERVICES_H
#include "filesystem.h"
#include <stdint.h>
uintptr_t opencfw_boot_file_open(uintptr_t path,uintptr_t mode);
uint32_t opencfw_boot_file_read(void *,uint32_t,uint32_t,uintptr_t);
uint32_t opencfw_boot_file_prepare(uintptr_t,uint32_t,uint32_t);
uint32_t opencfw_boot_file_close(uintptr_t);
void *opencfw_boot_fs_alloc(uint32_t);
void opencfw_boot_fs_free(void *);
uint32_t opencfw_boot_fs_mutex_acquire(uintptr_t,uint32_t);
void opencfw_boot_fs_mutex_release(uintptr_t);
#ifdef OPENCFW_BOOT_FS_TEST
extern lfs_t *opencfw_boot_test_fs;
extern uintptr_t opencfw_boot_test_mutex;
#endif
#endif
