/* SPDX-License-Identifier: MIT */
/* Reconstructed from locked Apollo instructions; upstream confirms names and
 * two-stage registers, not stock compiled-byte identity or physical ownership. */
#include "rearm.h"
static uint32_t word(const volatile void *h, uint32_t off)
{ return *(const volatile uint32_t *)((const volatile uint8_t *)h + off); }
static void set_word(volatile void *h, uint32_t off, uint32_t value)
{ *(volatile uint32_t *)((volatile uint8_t *)h + off) = value; }
static volatile uint32_t *peripheral(uint32_t module, uint32_t off)
{ return (volatile uint32_t *)(uintptr_t)(0x40208000u + (module << 12) + off); }
uint32_t opencfw_i2s_dma_error(const volatile void *handle, uint32_t direction)
{
    uint32_t module = word(handle, 4);
    *peripheral(module, 0x200) = 0;
    if ((uint8_t)direction == 0) *peripheral(module, 0x20c) = 0;
    else if ((uint8_t)direction == 1) *peripheral(module, 0x218) = 0;
    return 0;
}
uint32_t opencfw_i2s_ipb_service(const volatile void *handle)
{
    uint32_t module = word(handle, 4);
    volatile uint32_t *reg = peripheral(module, 0x4c);
    uint32_t snapshot = *reg;
    if (snapshot & 0x80000u) *reg = *reg & ~0x80000u;
    if (snapshot & 0x20000u) *reg = *reg & ~0x20000u;
    if (snapshot & 0x40000u) *reg = *reg & ~0x40000u;
    if (snapshot & 0x10000u) *reg = *reg & ~0x10000u;
    return 0;
}
uint32_t opencfw_i2s_interrupt_service(volatile void *handle, uint32_t status)
{
    uint32_t module = word(handle, 4);
    if (*peripheral(module, 0x218) & 4u) opencfw_i2s_dma_error(handle, 1);
    if (*peripheral(module, 0x20c) & 4u) opencfw_i2s_dma_error(handle, 0);
    if ((status & 0x10u) && word(handle, 0x40) != 0xffffffffu) {
        *peripheral(module, 0x20c) = *peripheral(module, 0x20c) & ~2u;
        if (*peripheral(module, 0x21c) & 1u) return 9;
        uint32_t selected = word(handle, 0x4c);
        uint32_t pong = word(handle, 0x40);
        uint32_t next = selected == pong ? word(handle, 0x3c) : pong;
        set_word(handle, 0x4c, next);
        *peripheral(module, 0x224) = next;
        *peripheral(module, 0x220) = word(handle, 0x54) >> 2;
        *peripheral(module, 0x21c) = *peripheral(module, 0x21c) | 1u;
    }
    if ((status & 8u) && word(handle, 0x48) != 0xffffffffu) {
        *peripheral(module, 0x218) = *peripheral(module, 0x218) & ~2u;
        if (*peripheral(module, 0x21c) & 2u) return 9;
        uint32_t selected = word(handle, 0x50);
        uint32_t pong = word(handle, 0x48);
        uint32_t next = selected == pong ? word(handle, 0x44) : pong;
        set_word(handle, 0x50, next);
        *peripheral(module, 0x22c) = next;
        *peripheral(module, 0x228) = word(handle, 0x58) >> 2;
        *peripheral(module, 0x21c) = *peripheral(module, 0x21c) | 2u;
    }
    if (status & 1u) opencfw_i2s_ipb_service(handle);
    return 0;
}
static uint32_t valid(const volatile void *handle)
{ return (word(handle, 0) & 0x01ffffffu) == 0x01125125u; }
uint32_t opencfw_i2s_interrupt_status(const volatile void *handle, uint32_t *status, uint32_t enabled_only)
{
    uint32_t module = word(handle, 4);
    if (!valid(handle)) return 2;
    *status = *peripheral(module, 0x304);
    if ((uint8_t)enabled_only) *status = *status & *peripheral(module, 0x300);
    return 0;
}
uint32_t opencfw_i2s_interrupt_clear(const volatile void *handle, uint32_t status)
{
    uint32_t module = word(handle, 4);
    if (!valid(handle)) return 2;
    *peripheral(module, 0x308) = status;
    (void)*peripheral(module, 0x304);
    return 0;
}
static volatile void *audio_handle(void)
{ return (volatile void *)(uintptr_t)*(volatile uint32_t *)(uintptr_t)0x2007450cu; }
uint32_t opencfw_audio_i2s_irq_prefix(void)
{
    uint32_t status;
    /* As in stock ISR, initialized handle is a precondition; failures of
     * status_get would leave the local undefined and are outside this seam. */
    (void)opencfw_i2s_interrupt_status(audio_handle(), &status, 1);
    (void)opencfw_i2s_interrupt_clear(audio_handle(), status);
    (void)opencfw_i2s_interrupt_service(audio_handle(), status);
    return status;
}
