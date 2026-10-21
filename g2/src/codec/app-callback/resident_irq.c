/* SPDX-License-Identifier: MIT
 * GX8002 image-A resident critical-section ABI, reconstructed from the
 * authenticated 0x10025560 and 0x1002556c instruction bodies.
 * CR0 carries the previous interrupt state; restoring the entire value is
 * essential because the caller preserves it across the protected operation.
 */
#include <stdint.h>

uint32_t g2_codec_critical_save(void)
{
    uint32_t state;
    __asm__ volatile(
        "mfcr %0, cr<0, 0>\n\t"
        "psrclr ie"
        : "=r"(state)
        :
        : "memory");
    return state;
}

void g2_codec_critical_restore(uint32_t state)
{
    __asm__ volatile("mtcr %0, cr<0, 0>" : : "r"(state) : "memory");
}

extern void gx8002_resident_vic_enable_irq_254ac(uint32_t number);

/* 0x100254c8: the VIC clear-enable bank is 32 words after set-enable. */
void gx8002_resident_vic_disable_irq_254c8(uint32_t number)
{
    volatile uint32_t *const vic =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    vic[((number >> 5) & 3u) + 32u] = UINT32_C(1) << (number & 31u);
}

/* 0x100254e4: restore the two enable words captured by save-disable. */
void gx8002_resident_irq_restore_enabled_254e4(void)
{
    volatile uint32_t *const saved =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20026eec);
    volatile uint32_t *const vic =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    vic[0] = saved[0];
    vic[1] = saved[1];
}

/* 0x100254fc and 0x10025504 are genuine call/return wrappers. */
void gx8002_resident_mask_irq_254fc(uint32_t number)
{
    gx8002_resident_vic_disable_irq_254c8(number);
}

void gx8002_resident_unmask_irq_25504(uint32_t number)
{
    gx8002_resident_vic_enable_irq_254ac(number);
}

/* 0x1002550c: snapshot two enable registers, mask IRQs 0..31. */
void gx8002_resident_irq_save_disable_2550c(void)
{
    volatile uint32_t *const saved =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20026eec);
    volatile uint32_t *const vic =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000e100);
    saved[0] = vic[0];
    saved[1] = vic[1];
    for (uint32_t number = 0; number < 32u; ++number)
        gx8002_resident_vic_disable_irq_254c8(number);
}

/* 0x10025534: another call/return entry to save-disable. */
void gx8002_resident_irq_save_disable_wrapper_25534(void)
{
    gx8002_resident_irq_save_disable_2550c();
}
