/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_AEABI_MEMCPY_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_AEABI_MEMCPY_H

typedef unsigned int open_cfw_bootloader_memcpy_size;

void open_cfw_bootloader_aeabi_memcpy(
    void *destination,
    const void *source,
    open_cfw_bootloader_memcpy_size count
);

#endif
