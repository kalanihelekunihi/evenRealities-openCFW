/* SPDX-License-Identifier: MIT */
/* Reconstructed NPU status-to-event mapping. Preserve ordered output RMWs
 * and observed final r0 (status bit16), without claiming a private SDK type.
 * Candidate pending qualification. */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_reg_get_value(volatile uint32_t *);
uint32_t open_cfw_gx8002_npu_get_interrupt(void *base, volatile uint32_t *events)
{
    uint32_t status = open_cfw_gx8002_reg_get_value((volatile uint32_t *)((uintptr_t)base + 12u));
    uint32_t initial = status & 1u;
    if (status & UINT32_C(0x10)) initial |= 2u;
    *events = initial;
    if (status & UINT32_C(0x100)) *events |= 4u;
    if (status & UINT32_C(0x1000)) *events |= 8u;
    if (status & UINT32_C(0x2000)) *events |= 16u;
    if (status & UINT32_C(0x4000)) *events |= 32u;
    if (status & UINT32_C(0x10000)) *events |= 64u;
    return status & UINT32_C(0x10000);
}
