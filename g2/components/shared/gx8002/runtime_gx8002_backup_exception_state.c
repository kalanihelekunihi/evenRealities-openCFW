/* SPDX-License-Identifier: MIT */
#include "backup_exception_state.h"
/* Original BSS span 0x20017090..0x20017390. The entry switches to its
 * upper boundary and subtracts a frame before storing registers.
 */
__attribute__((section(".bss.backup_exception_stack"),aligned(4)))
uint32_t open_cfw_gx8002_backup_exception_stack[192];
__attribute__((section(".bss.backup_interrupted_sp"),aligned(4)))
volatile uint32_t open_cfw_gx8002_backup_interrupted_sp;
