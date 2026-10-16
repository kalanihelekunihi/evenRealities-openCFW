/* Terminal query dialog session-name lookup, stock 0x5ec7f0..0x5ec829. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* observed 0x2006e0d0 */
extern uint8_t *audio_td_active_session(void);

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

const char *audio_terminal_query_session_name_5ec7f0(void) {
    const uint8_t *active = audio_td_active_session();
    const uint32_t session = load_u32(audio_terminal_ui_state_base + 0x288u);
    if (active == 0)
        return 0;
    const uint32_t count = load_u32(active + 8u);
    for (uint32_t i = 0; i < count; ++i) {
        const uint8_t *entry = active + 0x9cu + i * 0x90u;
        if (load_u32(entry) == session &&
            ((uint16_t)entry[4] | ((uint16_t)entry[5] << 8)) != 0u)
            return (const char *)(entry + 6u);
    }
    return 0;
}
