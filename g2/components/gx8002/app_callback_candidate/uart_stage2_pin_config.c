/* SPDX-License-Identifier: MIT
 * Direct native pin match 0x10005000, setter 0x10005044, and
 * default-table loader 0x10005094. Defaults are 31 exact pin/value
 * pairs from stock initialized data at 0x1000825d.
 */
#include <stdint.h>

struct pin_start_value { uint8_t pin; uint8_t value; };
_Static_assert(sizeof(struct pin_start_value) == 2, "pin/value ABI");

__attribute__((section(".stage2.pin.defaults"), used))
static const struct pin_start_value default_pins[31] = {
    {0,1}, {0,2}, {0,3}, {0,4}, {0,5}, {0,6}, {0,7}, {0,8},
    {0,9}, {0,10}, {0,11}, {0,12}, {0,13}, {0,14}, {0,15},
    {0,16}, {0,17}, {0,18}, {0,19}, {0,20}, {0,21}, {0,22},
    {0,23}, {0,24}, {0,25}, {0,26}, {0,27}, {0,28},
    {0,29}, {0,30}, {0,31},
};

uint32_t gx8002_uart_stage2_pin_matches_5000(int32_t pin, int32_t value)
{
    if (pin < 0 || value < 0) return UINT32_MAX;
    uint32_t actual = 255u;
    if (pin < 33) {
        volatile uint32_t *const mux =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010090);
        const uint32_t shift = ((uint32_t)pin & 7u) * 4u;
        actual = (mux[(uint32_t)pin >> 3] >> shift) & 15u;
    }
    return (uint32_t)value == actual ? 0u : UINT32_MAX;
}

uint32_t gx8002_uart_stage2_pin_write_5044(uint32_t pin, int32_t value)
{
    if (pin >= 33u) return UINT32_MAX;
    volatile uint32_t *const mux =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010090);
    volatile uint32_t *const word = &mux[pin >> 3];
    const uint32_t shift = (pin & 7u) * 4u;
    const uint32_t mask = 15u << shift;
    const uint32_t before = *word;
    *word = (before & ~mask) | (((uint32_t)value & 15u) << shift);
    if (value < 0) return UINT32_MAX;
    return (((*word & mask) >> shift) == (uint32_t)value) ? 0u : UINT32_MAX;
}

uint32_t gx8002_uart_stage2_pin_prepare_5094(
    const struct pin_start_value *pins, uint32_t count)
{
    if (pins == 0 || count == 0) return UINT32_MAX;
    for (uint32_t i = 0; i < 31u; ++i) {
        const uint8_t pin = default_pins[i].pin;
        uint8_t value = default_pins[i].value;
        for (uint32_t j = 0; j < count; ++j) {
            if (pins[j].pin == pin) { value = pins[j].value; break; }
        }
        (void)gx8002_uart_stage2_pin_write_5044(pin, value);
    }
    return 0;
}
