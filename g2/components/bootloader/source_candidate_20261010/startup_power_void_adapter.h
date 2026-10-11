/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_STARTUP_POWER_VOID_ADAPTER_H
#define OPENCFW_BOOT_STARTUP_POWER_VOID_ADAPTER_H
/* Caller at stock 0x41fa50 invokes the root with no declared arguments and
 * ignores its return. Raw registers and R5/R7 still belong to the ABI. */
void opencfw_boot_startup_power_initialize(void);
#endif
