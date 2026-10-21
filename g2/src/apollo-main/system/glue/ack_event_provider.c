#include <stdint.h>

/* Original 0x4c9c3c: post bit (1 << index) to the retained manager
 * event group through osEventFlagsSet. The stop-handshake receipt shows
 * this is an audio acknowledgment before timer and queue cleanup. */
extern uint32_t osEventFlagsSet(void *group, uint32_t bits);

void audio_ack_index(uint32_t index) {
    uint32_t amount = (uint8_t)index;
    uint32_t bits = amount < 32u ? (1u << amount) : 0u;
    void *group = *(void *volatile *)(uintptr_t)0x200040f4u;
    (void)osEventFlagsSet(group, bits);
}

void audio_exit_request(uint32_t index) __attribute__((alias("audio_ack_index")));
