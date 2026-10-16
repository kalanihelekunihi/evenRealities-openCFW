/* Stock Apollo Main ALS manual target scale, 0x4addb6..0x4ade36. */
#include <stdint.h>

extern uint32_t audio_als_first_curve_percent_4ad9e2(void);
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t, uint32_t,
                                                uint32_t, uint32_t);

uint32_t audio_als_manual_target_scale_4addb6(uint32_t nominal,
                                               uint32_t requested)
{
    uint32_t first = audio_als_first_curve_percent_4ad9e2();
    if (requested < first)
        requested = first;
    if (requested >= 100u)
        requested = 100u;
    uint32_t denominator = nominal - first;
    uint32_t difference = requested > first ? requested - first : 0u;
    if (denominator == 0u)
        return 1024u;
    uint64_t numerator = ((uint64_t)difference << 10) +
                         (uint64_t)(denominator >> 1);
    uint32_t result = (uint32_t)audio_uart_ring_u64_div_47cc60(
        (uint32_t)numerator, (uint32_t)(numerator >> 32), denominator, 0u);
    if (result < 615u)
        result = 614u;
    if (result >= 1434u)
        result = 1434u;
    return result;
}
