/* SPDX-License-Identifier: MIT
 * Isolated caller-compatible entry for startup root 0x41c4b4.
 * The branch preserves all raw registers, including ambient callee-saved R5
 * and R7. The imported target is the existing validated source ABI adapter
 * (`startup_root_entry.S`), not the four-parameter Ghidra C sketch.
 */
#include "startup_power_void_adapter.h"

__attribute__((naked)) void opencfw_boot_startup_power_initialize(void)
{
    __asm__ volatile("b.w opencfw_boot_startup_initialize_abi");
}
