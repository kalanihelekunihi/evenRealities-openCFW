/* Native td_ring_index_wrap 0x5970a8 and td_session_find_by_id 0x59726e. */
#include <stdint.h>

static uint16_t load16(const uint8_t *p) {
    return (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
}
static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 |
           (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}

uint32_t audio_td_ring_index_wrap(uint8_t *ring, uint16_t logical_index) {
    return ((uint32_t)logical_index + load16(ring + 0x8502u)) % 64u;
}

uint32_t audio_td_session_find_by_id(uint8_t *ring, uint32_t session,
                                      uint16_t *logical_index) {
    if (ring == 0 || logical_index == 0 || session == 0u) return 0u;
    int16_t count = (int16_t)load16(ring + 0x8500u);
    if (count == 0) return 0u;
    for (int16_t remaining = count; remaining != 0; --remaining) {
        uint16_t index = (uint16_t)(remaining - 1);
        uint32_t physical = audio_td_ring_index_wrap(ring, index);
        if (load32(ring + physical * 0x214u + 0x208u) == session) {
            *logical_index = index;
            return 1u;
        }
    }
    return 0u;
}
