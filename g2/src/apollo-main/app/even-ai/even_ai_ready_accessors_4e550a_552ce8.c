/* Small stock accessors called by EvenAI async update. */
#include <stdint.h>

extern uint8_t audio_even_ai_ready_state_2006f138[0x218];

const char audio_text_stream_empty_552cf4[1]
    __attribute__((section(".rodata.opencfw.evenai.pending.empty"), used)) = {0};

uint8_t audio_even_ai_stream_interval_get_4e550a(void) {
    uint8_t interval = audio_even_ai_ready_state_2006f138[8];
    return interval == 0u ? 25u : interval;
}

const char *audio_text_stream_pending_text_552ce8(uint32_t handle) {
    if (handle == 0u)
        return audio_text_stream_empty_552cf4;
    uint32_t address;
    __builtin_memcpy(&address, (const void *)(uintptr_t)(handle + 4u), 4u);
    return (const char *)(uintptr_t)address;
}
