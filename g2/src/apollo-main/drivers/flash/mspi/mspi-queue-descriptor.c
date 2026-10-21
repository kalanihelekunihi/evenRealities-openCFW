/* SPDX-License-Identifier: MIT
 * Main 0x4bfdf4: load the next MSPI queue descriptor.
 */
#include <stdint.h>

extern uint32_t g2_main_mspi_clock_acquire_4c44bc(uint32_t, uint32_t);

uint64_t g2_main_mspi_queue_descriptor_4bfdf4(uint32_t controller,
                                                uint32_t second,
                                                uint32_t third,
                                                uint32_t high)
{
    (void)second;
    (void)third;
    const volatile uint8_t *const handle =
        (const volatile uint8_t *)(uintptr_t)controller;
    const uint32_t module =
        *(const volatile uint32_t *)(const void *)(handle + 4u);
    const uint32_t divisor =
        *(const volatile uint32_t *)(const void *)(handle + 0x848u);
    const uint32_t next =
        *(const volatile uint32_t *)(const void *)(handle + 0x850u) + 1u;
    const uint32_t descriptors =
        *(const volatile uint32_t *)(const void *)(handle + 0x854u);
    const volatile uint32_t *const item =
        (const volatile uint32_t *)(uintptr_t)
        (descriptors + (next % divisor) * 0x18u);
    const uint32_t result = g2_main_mspi_clock_acquire_4c44bc(
        4u, (module + 0x10u) & 0xffu);
    if (result == 0u) {
        volatile uint32_t *const registers =
            (volatile uint32_t *)(uintptr_t)
            (UINT32_C(0x40060000) + module * 0x1000u);
        registers[0x100u / 4u] = 0u;
        registers[0x108u / 4u] = item[0];
        registers[0x10cu / 4u] = item[1];
        registers[0x110u / 4u] = item[2];
        registers[0x100u / 4u] = item[3];
    }
    return ((uint64_t)high << 32) | result;
}
