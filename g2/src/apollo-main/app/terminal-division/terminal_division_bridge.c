/* Compatibility for the previously selected terminal object. */
#include <stdint.h>

extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t, uint32_t,
                                               uint32_t, uint32_t);

uint32_t audio_u64_divide_1000(uint32_t low, uint32_t high,
                               uint32_t divisor_low, uint32_t divisor_high) {
    return (uint32_t)audio_uart_ring_u64_div_47cc60(low, high,
                                                     divisor_low, divisor_high);
}
