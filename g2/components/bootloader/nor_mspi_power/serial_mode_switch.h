/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_NOR_SERIAL_MODE_SWITCH_H
#define OPENCFW_NOR_SERIAL_MODE_SWITCH_H

#include <stdint.h>

/* Readable provider for locked entry 0x420c5c. */
uint32_t opencfw_provider_420c5c(uint32_t mode);

#endif
