/* SPDX-License-Identifier: MIT
 * Stock 0x0800a074 three-sample 16-bit sensor reader.
 * Read adapter and delay remain controlled lower contracts.
 */
#include <stdint.h>

extern uint32_t case_binary_sensor_read_adapter(uint32_t selector,
                                                 uint8_t *destination,
                                                 uint32_t length);
extern uint32_t case_binary_sensor_delay_count(uint32_t count);

/* Stock 0x0800A074 (case_read_stable_u16) */
uint32_t case_binary_read_word_lower(uint32_t selector, uint32_t *out)
{
    uint8_t sample[4] = {0, 0, 0, 0};
    if (case_binary_sensor_read_adapter(selector, sample, 2u) != 0u)
        return 0xffffffffu;
    uint32_t first = ((uint32_t)sample[0] << 8) | sample[1];
    case_binary_sensor_delay_count(5u);
    if (case_binary_sensor_read_adapter(selector, sample, 2u) != 0u)
        return 0xffffffffu;
    uint32_t second = ((uint32_t)sample[0] << 8) | sample[1];
    if (first == second) {
        *out = first;
        return 0u;
    }
    case_binary_sensor_delay_count(5u);
    if (case_binary_sensor_read_adapter(selector, sample, 2u) != 0u)
        return 0xffffffffu;
    *out = ((uint32_t)sample[0] << 8) | sample[1];
    return 0u;
}
