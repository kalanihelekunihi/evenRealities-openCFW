/* SPDX-License-Identifier: MIT
 * Stock 0x416200 provider name used by selected event and teardown callers.
 * The selected provider uses a 64-bit return to carry stock R0 status and
 * preserved incoming R3 in R1. Callers of these historical aliases declare
 * a void one-argument API; branch without changing their input registers.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_provider_416200(uintptr_t handle)
{
    __asm__ volatile("b.w opencfw_boot_runtime_action");
}

__attribute__((naked)) void opencfw_boot_dfu_thread_terminate(uint32_t handle)
{
    __asm__ volatile("b.w opencfw_boot_runtime_action");
}
