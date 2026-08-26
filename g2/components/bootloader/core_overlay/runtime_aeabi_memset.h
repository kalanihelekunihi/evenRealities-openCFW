/* SPDX-License-Identifier: GPL-3.0-or-later */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_AEABI_MEMSET_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_AEABI_MEMSET_H

typedef __SIZE_TYPE__ open_cfw_bootloader_memset_size;

void open_cfw_bootloader_aeabi_memset(
    void *destination,
    open_cfw_bootloader_memset_size count,
    int value
);

#endif
