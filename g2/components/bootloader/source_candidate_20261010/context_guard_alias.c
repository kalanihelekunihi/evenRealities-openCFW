/* SPDX-License-Identifier: MIT
 * Historical callable entry at stock 0x41602a. Selected C guard owns the
 * IPSR, scheduler-mode, PRIMASK and BASEPRI decision.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_provider_41602a(void)
{
    __asm__ volatile("b.w opencfw_bl_context_guard");
}
