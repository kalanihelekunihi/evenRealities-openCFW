/* Stock ANCC state packet and paired send, 0x497cf0. */
#include <stdint.h>

extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t, const void *,
                                                     uint32_t, uint32_t, uint32_t);

void audio_even_ai_ancc_state_sync_497cf0(uint32_t state, uint32_t delay) {
    uint8_t packet[8] = {1u, 0u, 0u, 0u, 0u, 0u, 0u, 0u};
    packet[1] = (uint8_t)state;
    for (uint32_t index = 0; index < 4u; ++index)
        packet[2u + index] = (uint8_t)(delay >> (index * 8u));
    (void)audio_sync_send_to_both_ext_464f76(4u, packet, 6u, 0u, 5u);
}
