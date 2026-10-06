/* SPDX-License-Identifier: MIT
 * Source reconstruction of locked private helper 0x4249a0. The clock
 * control register address and update order come from the helper's literal
 * loads and stores, not from the public 52-byte MSPI configuration ABI.
 */
#include <stdint.h>

#define CLKGEN_MSPIOUTPUT 0x40004110u

extern void opencfw_hal_delay_us(uint32_t duration); /* stock 0x41d1c0 */

uint32_t opencfw_bl_mspi_clockgen_control(uint32_t module_register,
                                           uint32_t enable_register,
                                           uint32_t configure_register,
                                           uint32_t source_register)
{
    const uint8_t module = (uint8_t)module_register;
    const uint8_t enable = (uint8_t)enable_register;
    const uint8_t configure = (uint8_t)configure_register;
    const uint8_t source = (uint8_t)source_register;
    const uint32_t shift = ((uint32_t)module * 5u) & 0xffu;
    uint32_t previous;
    __asm volatile("mrs %0, primask\n\tcpsid i"
                   : "=r"(previous) :: "memory");

    volatile uint32_t *const reg =
        (volatile uint32_t *)(uintptr_t)CLKGEN_MSPIOUTPUT;
    uint32_t value = *reg;
    if (enable == 0u) {
        const uint32_t bit = shift < 32u ? (1u << shift) : 0u;
        value &= ~bit;
        *reg = value;
    } else {
        if (configure != 0u) {
            const uint32_t mask = shift < 32u ? (0x1eu << shift) : 0u;
            value &= ~mask;
            const uint32_t selection = shift < 32u
                ? (((uint32_t)source << 1u) << shift) : 0u;
            value |= selection;
            *reg = value;
        }
        const uint32_t bit = shift < 32u ? (1u << shift) : 0u;
        value = *reg | bit;
        *reg = value;
        opencfw_hal_delay_us(10u);
    }

    __asm volatile("msr primask, %0" :: "r"(previous) : "memory");
    return previous;
}
