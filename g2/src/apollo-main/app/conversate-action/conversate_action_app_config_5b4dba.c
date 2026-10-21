/* Native conversate_action_app_config 0x5b4dba..0x5b4e97. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern void audio_conversate_apply_config_5b133c(void);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_app_config";
static const char null_message[] = "pData is NULL";
static const char null_short[] = "[conversate]pData is NULL";
static const char config_message[] =
    "ai cue: %d, transcribe: %d, auto_pop_en: %d, use_audio: %d, cue_duration: %d";
static const char config_short[] =
    "[conversate]ai cue: %d, transcribe: %d, auto_pop_en: %d, use_audio: %d, cue_duration: %d";

uint32_t audio_conversate_action_5b4dba(void *context, const void *arg1,
                                           void *arg2) {
    (void)arg2;
    if (!arg1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 209u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    const uint8_t *const packet = (const uint8_t *)arg1;
    uint8_t *const state = (uint8_t *)context;
    if (packet[1] != 0u) {
        (void)audio_queue_copy_bytes(state + 1, packet + 2, 5u);
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 216u, config_message,
                               state[1], state[2], state[3], state[4], state[5]);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x0d400000u, config_short, config_short,
                             state[1], state[2], state[3], state[4], state[5]);
        audio_conversate_apply_config_5b133c();
    }
    audio_conversate_report_5b02e4(16u, 0u);
    return 0u;
}
