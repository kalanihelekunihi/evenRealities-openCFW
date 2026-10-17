/* Native Conversate cleanup timer predicate 0x5b3628..0x5b3647. */
#include <stdint.h>

uint32_t audio_conversate_timer_expired_5b3628(const uint8_t *timer,
                                                uint32_t tick) {
    if (timer == 0 || timer[0] == 0u)
        return 0u;
    uint32_t deadline = *(const uint32_t *)(const void *)(timer + 4u);
    return (int32_t)(tick - deadline) >= 0 ? 1u : 0u;
}
