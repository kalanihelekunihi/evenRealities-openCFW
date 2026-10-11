/* SPDX-License-Identifier: MIT
 * Locked GPIO interrupt status 0x41df48, clear 0x41dfc6 and callback
 * dispatch 0x41e09a. MMIO W1C and asynchronous edges need hardware proof.
 */
#include <stdint.h>

#define WORD(address) (*(volatile uint32_t *)(uintptr_t)(address))

static uint32_t valid_irq(uint32_t irq)
{
    return (irq - 56u < 7u) || (irq - 125u < 7u);
}

static uint32_t group_index(uint32_t irq)
{
    return irq - (irq < 63u ? 56u : 125u);
}

uint32_t opencfw_boot_gpio_irq_status(uint32_t irq, uint32_t enabled,
                                      uint32_t *output)
{
    if (output == 0 || !valid_irq(irq))
        return 6u;
    uint32_t primask;
    __asm__ volatile("mrs %0, primask\n cpsid i" : "=r"(primask) :: "memory");
    const uint32_t bank = irq >= 125u;
    const uintptr_t base = UINT32_C(0x40010530) + bank * 0x70u +
                           group_index(irq) * 0x10u;
    const uint32_t mask = enabled ? WORD(base) : UINT32_MAX;
    *output = WORD(base + 4u) & mask;
    uint32_t ipsr, control;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    __asm__ volatile("mrs %0, control" : "=r"(control));
    if (ipsr != 0u || (control & 1u) == 0u)
        __asm__ volatile("msr primask, %0" :: "r"(primask) : "memory");
    return 0u;
}

uint32_t opencfw_boot_gpio_irq_clear(uint32_t irq, uint32_t status)
{
    if (!valid_irq(irq))
        return 6u;
    const uint32_t bank = irq >= 125u;
    WORD(UINT32_C(0x40010538) + bank * 0x70u +
         group_index(irq) * 0x10u) = status;
    return 0u;
}

uint32_t opencfw_boot_gpio_irq_service(uint32_t irq, uint32_t status)
{
    if (!valid_irq(irq))
        return 5u;
    const uint32_t index = irq < 63u ? irq - 56u : irq - 125u + 7u;
    uint32_t result = 0u;
    while (status != 0u) {
        const uint32_t bit = (uint32_t)__builtin_ctz(status);
        status &= ~(1u << bit);
        const uintptr_t callback_address = UINT32_C(0x20023600) +
                                           index * 0x80u + bit * 4u;
        const uintptr_t argument_address = UINT32_C(0x20023d00) +
                                           index * 0x80u + bit * 4u;
        const uintptr_t callback = WORD(callback_address);
        if (callback == 0u)
            result = 7u;
        else
            ((void (*)(uint32_t))callback)(WORD(argument_address));
    }
    return result;
}
