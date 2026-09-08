/* SPDX-License-Identifier: MIT */
/* Reconstructed mask-to-register-bit mapping from stock NPU routines.
 * Preserve each primitive call and its order. Candidate pending qualification. */
#include <stdint.h>
extern void open_cfw_gx8002_reg_set_bit(volatile uint32_t *, uint32_t);
#define APPLY(flag, bit) do { if (mask & (flag)) open_cfw_gx8002_reg_set_bit(reg, (bit)); } while (0)
void open_cfw_gx8002_npu_en_interrupt(void *base, uint32_t mask)
{
    volatile uint32_t *reg = (volatile uint32_t *)((uintptr_t)base + 4u);
    APPLY(1u, 0); APPLY(2u, 4); APPLY(4u, 8); APPLY(8u, 12);
    APPLY(16u, 13); APPLY(32u, 14); APPLY(64u, 16);
}
void open_cfw_gx8002_npu_clr_interrupt(void *base, uint32_t mask)
{
    volatile uint32_t *reg = (volatile uint32_t *)((uintptr_t)base + 8u);
    APPLY(1u, 0); APPLY(2u, 4); APPLY(4u, 8); APPLY(8u, 12);
    APPLY(16u, 13); APPLY(32u, 14); APPLY(64u, 16);
}
void open_cfw_gx8002_npu_clr_interrupt_without_overflow(void *base, uint32_t mask)
{
    volatile uint32_t *reg = (volatile uint32_t *)((uintptr_t)base + 8u);
    APPLY(1u, 0); APPLY(2u, 4); APPLY(4u, 8); APPLY(8u, 12);
    APPLY(64u, 16);
}
void open_cfw_gx8002_npu_clr_overflow_interrupt(void *base, uint32_t mask)
{
    volatile uint32_t *reg = (volatile uint32_t *)((uintptr_t)base + 8u);
    APPLY(16u, 13); APPLY(32u, 14);
}
