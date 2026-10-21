/* Native conversate_action_transcribe_data 0x5b5428..0x5b55a7. */
#include <stdint.h>

extern uint32_t audio_conversate_ui_state_get_5b16d0(void);
extern void audio_conversate_transcribe_update_5b41be(const void *);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_transcribe_data";
static const char null_message[] = "conversate transcribe data is NULL";
static const char null_short[] = "[conversate]conversate transcribe data is NULL";
static const char not_running[] =
    "conversate state is not running, no need to update transcribe data";
static const char not_running_short[] =
    "[conversate]conversate state is not running, no need to update transcribe data";
static const char invalid_state[] =
    "conversate ui state is invalid, no need to update transcribe data";
static const char invalid_state_short[] =
    "[conversate]conversate ui state is invalid, no need to update transcribe data";
static const char received[] = "transcribe data received: len=%d, end_flag=%d";
static const char received_short[] =
    "[conversate]transcribe data received: len=%d, end_flag=%d";
static const char text_short[] = "[conversate]%s";

uint32_t audio_conversate_action_5b5428(const void *context, const void *arg1,
                                           void *arg2) {
    (void)arg2;
    if (!arg1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 374u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    if (((const uint8_t *)context)[0] != 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 379u, not_running);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, not_running_short, not_running_short);
        return UINT32_MAX;
    }
    const uint8_t state = (uint8_t)audio_conversate_ui_state_get_5b16d0();
    if (state == 0u || state == 6u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 385u, invalid_state);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, invalid_state_short, invalid_state_short);
        return UINT32_MAX;
    }
    const uint8_t *const packet = (const uint8_t *)arg1;
    const uint16_t length = (uint16_t)((uint16_t)packet[0] | ((uint16_t)packet[1] << 8));
    const uint32_t end_flag = *(const uint32_t *)(const void *)(packet + 0x404u);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 389u, received,
                           length, end_flag);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c800000u, received_short, received_short,
                         length, end_flag);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 390u, "%s", packet + 2);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c400000u, text_short, text_short, packet + 2);
    audio_conversate_transcribe_update_5b41be(arg1);
    audio_conversate_report_5b02e4(11u, 0u);
    return 0u;
}
