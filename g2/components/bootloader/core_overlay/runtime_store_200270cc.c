/* SPDX-License-Identifier: GPL-3.0-or-later */

#include "runtime_store_200270cc.h"

#ifndef OPEN_CFW_BOOTLOADER_STORE_200270CC_TARGET
#define OPEN_CFW_BOOTLOADER_STORE_200270CC_TARGET \
    ((volatile uint32_t *)(uintptr_t)UINT32_C(0x200270CC))
#endif

__attribute__((used, noinline))
void open_cfw_bootloader_store_200270cc(uint32_t value)
{
    *OPEN_CFW_BOOTLOADER_STORE_200270CC_TARGET = value;
}
