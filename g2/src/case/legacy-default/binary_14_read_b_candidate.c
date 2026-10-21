/* SPDX-License-Identifier: MIT
 * Stock 0x08009f18 mode-dependent signed sensor conversion.
 */
#include <stdint.h>

extern uint32_t case_binary_read_byte_lower(uint32_t selector, uint8_t *value);
extern uint32_t case_binary_read_word_lower(uint32_t selector, uint32_t *value);
extern uint32_t case_binary_14_scale(uint32_t value, uint32_t radix);

uint32_t case_binary_14_read_b(uint32_t *out)
{
    uint32_t raw = 0u;
    uint8_t mode = 0u;
    if (case_binary_read_byte_lower(0xabu, &mode) != 0u)
        return 0xffffffffu;
    if (case_binary_read_word_lower(14u, &raw) != 0u)
        return 0xffffffffu;
    uint32_t signed_sample = (uint32_t)(int32_t)(int16_t)(uint16_t)raw;
    if (mode == 0u) {
        *out = 0x1e240u;
    } else {
        uint32_t multiplier = (mode >> 6) != 0u ? 1600u : 3815u;
        *out = case_binary_14_scale(signed_sample * multiplier, 10000u);
    }
    return 0u;
}
