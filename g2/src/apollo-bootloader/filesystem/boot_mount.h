/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_MOUNT_H
#define OPENCFW_BOOT_MOUNT_H
#include <stdint.h>

/* Source replacement for the stock filesystem initializer at 0x00421210.
 * Return values are the stock initializer's 0/9 status; reset callers ignore
 * the value, but retaining it makes the provider independently testable. */
uint32_t opencfw_provider_421210(void);

#endif
