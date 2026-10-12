/* SPDX-License-Identifier: MIT
 * Native console selector at runtime SRAM 0x2002731c. This address is inside
 * the authenticated startup clear span [0x20026d80,0x2002ecec); the XIP
 * console selector writes it before the output body reads it. The final
 * linker must place this NOBITS word at the native runtime address.
 */
#include <stdint.h>

uint32_t gx8002_xip_console_port_2002731c
    __attribute__((section(".bss.gx8002.console_port.2731c"), used,
                   aligned(4)));
