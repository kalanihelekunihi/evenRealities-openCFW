/* Native service_even_ai_fn 0x498092: local EvenAI action decode.
 * Notification encoders and exact logging remain separate providers/gates.
 */
#include <stdint.h>

extern uint8_t audio_even_ai_service_state_2006ed10[0x218];
extern uint8_t audio_even_ai_config_state_20074974[3];
extern void audio_even_ai_state_lock_4e1fa6(void);
extern void audio_even_ai_state_unlock_4e1fbe(void);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_even_ai_encode_ctrl_4e3788(uint32_t, const void *);
extern uint32_t audio_even_ai_encode_vad_4e3b80(uint32_t, const void *);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "service.evenAI";
static const char source[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\evenAI\\service_even_ai.c";
static const char function[] = "SVC_DecodeLocalEvenAIInfo";
static const char invalid[] = "raw_data is NULL or len is 0";
static const char invalid_short[] = "[service.evenAI]raw_data is NULL or len is 0";
static const char startup[] = "recv evenai startup:%d";
static const char startup_short[] = "[service.evenAI]recv evenai startup:%d";
static const char stop[] = "recv evenai stop";
static const char stop_short[] = "[service.evenAI]recv evenai stop";
static const char vad[] = "recv vad status = %d";
static const char vad_short[] = "[service.evenAI]recv vad status = %d";
static const char action[] = "[evenai]action_id = %d, action_type = %d";
static const char action_short[] = "[service.evenAI][evenai]action_id = %d, action_type = %d";

static void log_event(uint8_t severity, uint32_t line, uint32_t format,
                      const char *message, const char *short_message,
                      uint32_t a, uint32_t b) {
    if (audio_log_level() & 2u)
        audio_log_extended(severity, module, source, function, line, message, a, b);
    uint32_t level = audio_log_level();
    if ((level & 1u) || (audio_log_level() & 4u))
        (void)compressed_log_output(format, short_message, short_message, a, b);
}

static void copy_four(uint8_t *destination, const uint8_t *source_bytes) {
    for (uint32_t i = 0; i < 4u; ++i)
        destination[i] = source_bytes[i];
}

int32_t audio_even_ai_local_decode_498092(uint32_t data, uint32_t length) {
    const uint8_t *p = (const uint8_t *)(uintptr_t)data;
    if (p == 0 || length == 0u) {
        log_event(1u, 0x103u, 0x04000000u, invalid, invalid_short, 0u, 0u);
        return -1;
    }
    uint8_t *state = audio_even_ai_service_state_2006ed10;
    if (p[0] == 2u) {
        if (p[1] == 1u) {
            log_event(3u, 0x10eu, 0x0c400000u, startup, startup_short, p[2], 0u);
            uint8_t notification[2] = {p[2], 0u};
            (void)audio_even_ai_encode_ctrl_4e3788(0u, notification);
            audio_even_ai_state_lock_4e1fa6();
            audio_uart_buffer_zero(state, 0x218u, 0u);
            state[0] = 1u;
            state[1] = 1u;
            state[2] = 1u;
            copy_four(state + 4u, p + 3u);
            audio_even_ai_config_state_20074974[1] = p[7];
            state[0x13] = p[8];
            state[0x14] = p[9];
            state[0x15] = p[10];
            audio_even_ai_state_unlock_4e1fbe();
        } else if (p[1] == 2u) {
            log_event(3u, 0x11fu, 0x0c000000u, stop, stop_short, 0u, 0u);
            audio_even_ai_state_lock_4e1fa6();
            state[1] = 1u;
            state[2] = 3u;
            audio_even_ai_state_unlock_4e1fbe();
        } else if (p[1] == 3u) {
            log_event(3u, 0x129u, 0x0c400000u, vad, vad_short, p[2], 0u);
            uint8_t notification[2] = {p[2], 0u};
            (void)audio_even_ai_encode_vad_4e3b80(0u, notification);
            audio_even_ai_state_lock_4e1fa6();
            state[1] = 2u;
            state[8] = p[2];
            audio_even_ai_state_unlock_4e1fbe();
        }
    } else if (p[0] == 7u) {
        audio_even_ai_state_lock_4e1fa6();
        state[1] = p[1];
        state[2] = p[2];
        audio_even_ai_state_unlock_4e1fbe();
        log_event(3u, 0x13bu, 0x0c800000u, action, action_short, state[1], state[2]);
    } else {
        return -1;
    }
    return 0;
}
