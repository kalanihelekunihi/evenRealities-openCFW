/* SPDX-License-Identifier: GPL-3.0-or-later */
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_MEMCMP_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_MEMCMP_H

typedef unsigned int open_cfw_bootloader_memcmp_size;

int open_cfw_bootloader_memcmp(
    const void *left,
    const void *right,
    open_cfw_bootloader_memcmp_size count
);

#endif
