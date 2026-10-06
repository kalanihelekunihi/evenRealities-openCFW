/* SPDX-License-Identifier: MIT - adapter to pinned BSD-licensed Ambiq HAL */
#include "am_mcu_apollo.h"
uint32_t opencfw_boot_mspi_interrupt_clear(void *handle,uint32_t mask) {
    return am_hal_mspi_interrupt_clear(handle,mask);
}
