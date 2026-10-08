/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_INITIALIZER_CALLBACKS_H
#define OPENCFW_BOOT_INITIALIZER_CALLBACKS_H

#include <stdint.h>

uint32_t opencfw_boot_init_callback_platform_sequence(void);
uint32_t opencfw_boot_init_callback_services(void);
uint32_t opencfw_boot_init_callback_redirect(void);

#endif
