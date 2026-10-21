/* Apollo main service_even_ai_fn at 0x497ea2, stock-derived state handoff.
 * The timer, lock/unlock, and final RAM placement are separate providers.
 */
#include <stdint.h>

extern void audio_even_ai_heartbeat_timer_start_4e304c(uint32_t);
extern void audio_even_ai_state_lock_4e1fa6(void);
extern void audio_even_ai_state_unlock_4e1fbe(void);
extern uint8_t audio_even_ai_service_state_2006ed10[0x218];
extern uint8_t audio_even_ai_config_state_20074974[3];

static uint16_t little16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static void copy_bytes(uint8_t *destination, const uint8_t *source, uint32_t length) {
    for (uint32_t i = 0; i < length; ++i)
        destination[i] = source[i];
}

static void set_text(const uint8_t *p, uint8_t opcode, uint32_t length_offset,
                     uint32_t text_offset) {
    uint8_t *state = audio_even_ai_service_state_2006ed10;
    uint16_t length = little16(p + length_offset);
    if (length > 0x200u)
        length = 0x200u;
    state[1] = opcode;
    state[0x16] = (uint8_t)length;
    state[0x17] = (uint8_t)(length >> 8);
    copy_bytes(state + 0x18, p + text_offset, length);
}

int32_t audio_even_ai_service_dispatch_497ea2(uint8_t opcode,
                                               const void *payload,
                                               uint32_t payload_length) {
    (void)payload_length;
    const uint8_t *p = payload;
    uint8_t *state = audio_even_ai_service_state_2006ed10;
    audio_even_ai_heartbeat_timer_start_4e304c(10000u);
    switch (opcode) {
    case 1u:
        if (p[0] == 1u)
            return 0;
        if (p[0] == 0u || p[0] > 3u)
            return -1;
        audio_even_ai_state_lock_4e1fa6();
        if (p[0] == 2u)
            state[0] = 1u;
        state[1] = 1u;
        state[2] = p[0];
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    case 2u:
        audio_even_ai_state_lock_4e1fa6();
        state[1] = 2u;
        audio_even_ai_state_unlock_4e1fbe();
        if (p[0] < 1u || p[0] > 3u)
            return -1;
        audio_even_ai_state_lock_4e1fa6();
        state[8] = p[0];
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    case 3u:
        audio_even_ai_state_lock_4e1fa6();
        set_text(p, 3u, 4u, 6u);
        state[0x10] = p[1];
        state[0x11] = p[2];
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    case 4u:
        audio_even_ai_state_lock_4e1fa6();
        state[1] = 4u;
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    case 5u:
        audio_even_ai_state_lock_4e1fa6();
        set_text(p, 5u, 4u, 6u);
        state[0x10] = p[1];
        state[0x11] = p[2];
        state[0x12] = p[0x207];
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    case 6u:
        audio_even_ai_state_lock_4e1fa6();
        set_text(p, 6u, 8u, 10u);
        state[2] = p[1];
        copy_bytes(state + 0x0c, p + 4u, 4u);
        state[0x12] = p[0x10b];
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    case 7u:
    case 8u:
        audio_even_ai_state_lock_4e1fa6();
        state[1] = opcode;
        state[2] = p[0];
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    case 9u:
        audio_even_ai_state_lock_4e1fa6();
        state[1] = 9u;
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    case 10u:
        audio_even_ai_state_lock_4e1fa6();
        state[1] = 10u;
        audio_even_ai_config_state_20074974[0] = p[0];
        audio_even_ai_config_state_20074974[1] = p[1];
        audio_even_ai_config_state_20074974[2] = p[3];
        audio_even_ai_state_unlock_4e1fbe();
        return 0;
    default:
        return -1;
    }
}
