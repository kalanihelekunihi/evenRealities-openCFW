/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOTLOADER_NOR_COMMANDS_H
#define OPENCFW_BOOTLOADER_NOR_COMMANDS_H

#include <stdint.h>

void opencfw_provider_42052a(void);
void opencfw_provider_420f10(void);
void opencfw_provider_4201ba(void);

uint32_t opencfw_provider_42069e(uint32_t instruction,
                                uint32_t address,
                                uint32_t send_address,
                                void *buffer,
                                uint32_t length);
uint32_t opencfw_provider_420e08(const void *device_config);

#endif
