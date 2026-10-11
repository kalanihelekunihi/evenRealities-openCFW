/* SPDX-License-Identifier: MIT
 * Native CASE hooks 0x08005c26, 0x08005e6c, 0x08005efc,
 * 0x08005efe each contain exactly
 * `bx lr`: preserve input R0 and perform no side effects.
 */
#include <stdint.h>

uint32_t case_boot_hook_5c26(uint32_t r0){return r0;}
uint32_t case_boot_hook_5e6c(uint32_t r0){return r0;}
uint32_t case_boot_hook_5efc(uint32_t r0){return r0;}
uint32_t case_boot_hook_5efe(uint32_t r0){return r0;}
