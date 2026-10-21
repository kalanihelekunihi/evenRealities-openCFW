/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x102049c8, 0x102049d8, 0x102050cc.
 * Direct C-SKY movih establishes AOUT MMIO base 0xa0b00000 (the retained
 * decompiler rendered its accesses at zero). Exact register operation
 * order and callback argument loads follow the native listing.
 */
#include <stdint.h>

static uint32_t load32(const volatile uint8_t *base, uint32_t offset)
{
    return *(volatile const uint32_t *)(const void *)(base + offset);
}
static void store32(volatile uint8_t *base, uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(void *)(base + offset) = value;
}

void gx8002_xip_aout_frame_over_enable_102049c8(
    volatile uint8_t *registers, uint32_t enabled)
{
    uint32_t old = load32(registers, 8u);
    store32(registers, 8u, (old & ~UINT32_C(2)) | ((enabled << 1u) & 2u));
}

void gx8002_xip_aout_play_check_idle_102049d8(
    volatile uint8_t *registers, uint32_t enabled)
{
    uint32_t old = load32(registers, 0u);
    store32(registers, 0u, (old & ~UINT32_C(2)) | ((enabled << 1u) & 2u));
}

uint32_t gx8002_xip_aout_handle_isr_102050cc(
    uint32_t irq, volatile uint8_t *context)
{
    if (irq != 13u) return 0u;
    volatile uint8_t *const aout =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0xa0b00000);
    uint32_t pending = load32(aout, 0x0cu) & load32(aout, 0x08u);
    if (pending & 4u) {
        store32(aout, 0x18u, load32(aout, 0x18u) & 0x3fffffffu);
        store32(aout, 0x0cu, load32(aout, 0x0cu) & 4u);
        store32(aout, 0x08u, load32(aout, 0x08u) & ~UINT32_C(4));
    }
    if (pending & 8u) {
        store32(aout, 0x1cu, load32(aout, 0x1cu) & 0x3fffffffu);
        store32(aout, 0x0cu, load32(aout, 0x0cu) & 8u);
        store32(aout, 0x08u, load32(aout, 0x08u) & ~UINT32_C(8));
    }
    if (pending & 0x40u)
        store32(aout, 0x0cu, load32(aout, 0x0cu) & 0x40u);
    if (pending & 1u) {
        store32(aout, 0x0cu, load32(aout, 0x0cu) & 1u);
        uint32_t raw = load32(context, 0x28u) & ~UINT32_C(1);
        if (raw) {
            void (*callback)(uint32_t, uint32_t) =
                (void (*)(uint32_t, uint32_t))(uintptr_t)raw;
            callback(load32(context, 0x20u), load32(context, 0x24u));
        }
    }
    if (pending & 2u) {
        store32(aout, 0x0cu, 0u);
        gx8002_xip_aout_play_check_idle_102049d8(aout, 0u);
        gx8002_xip_aout_frame_over_enable_102049c8(aout, 0u);
        store32(aout, 0x0cu, load32(aout, 0x0cu) & 2u);
        context[0x1cu] = 1u;
        uint32_t raw = load32(context, 0x2cu) & ~UINT32_C(1);
        if (raw) {
            void (*callback)(void) = (void (*)(void))(uintptr_t)raw;
            callback();
        }
    }
    return 0u;
}
