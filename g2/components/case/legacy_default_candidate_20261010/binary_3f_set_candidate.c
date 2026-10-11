/* SPDX-License-Identifier: MIT
 * Isolated stock 0x080099e8 shadowed output setter; program is a lower contract.
 */
#include <stdint.h>

extern uint32_t case_binary_3f_program(uint32_t index, uint32_t count,
                                       const uint8_t *value);

uint32_t case_binary_3f_set(uint32_t index, uint32_t value)
{
    volatile uint8_t *shadow = (volatile uint8_t *)(uintptr_t)0x20000090u;
    uint8_t desired = (uint8_t)value;
    uint32_t cached = shadow[index];
    if (cached == desired)
        return cached;
    uint32_t result = case_binary_3f_program(index, 1u, &desired);
    if (result != 0u) {
        shadow[index] = desired;
        return desired;
    }
    return result;
}
