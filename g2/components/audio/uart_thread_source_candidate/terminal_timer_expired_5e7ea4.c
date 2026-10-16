/* Stock Terminal timer deadline check 0x5e7ea4. */
#include <stdint.h>

uint32_t audio_terminal_timer_expired_5e7ea4(const uint8_t *timer,
                                               uint32_t tick) {
    if (timer == 0 || timer[0] == 0u)
        return 0u;
    uint32_t deadline = *(const uint32_t *)(const void *)(timer + 4u);
    return (int32_t)(tick - deadline) >= 0 ? 1u : 0u;
}
