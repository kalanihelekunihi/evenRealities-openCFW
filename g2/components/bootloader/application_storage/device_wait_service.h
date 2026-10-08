/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_DEVICE_WAIT_SERVICE_H
#define OPENCFW_BOOT_DEVICE_WAIT_SERVICE_H

#include <stdint.h>

uint32_t opencfw_boot_info_read_dispatch(uint32_t info_space,
                                        uint32_t word_offset,
                                        uint32_t word_count,
                                        volatile uint32_t *destination);

/* Compatibility symbol retained for the frozen mode-wait caller. */
uint32_t opencfw_boot_device_wait_service(uint32_t info_space,
                                         uint32_t word_offset,
                                         uint32_t word_count,
                                         volatile uint32_t *destination);

#endif
