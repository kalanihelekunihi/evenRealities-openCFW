/* SPDX-License-Identifier: MIT
 * Reconstructs stock 0x42d88a and 0x42dd68. This path does not initialize
 * scheduler, queue, or runtime state; the getter returns a literal value and
 * the wrapper discards it while returning the saved incoming R7. */
#include "runtime_context.h"

uint32_t opencfw_boot_dfu_runtime_context_get(void)
{
    return UINT32_C(0x00604000);
}

__attribute__((naked))
void opencfw_boot_dfu_runtime_context(void)
{
    __asm volatile(
        "push {r7, lr}\n"
        "bl opencfw_boot_dfu_runtime_context_get\n"
        "pop {r0, pc}\n");
}
