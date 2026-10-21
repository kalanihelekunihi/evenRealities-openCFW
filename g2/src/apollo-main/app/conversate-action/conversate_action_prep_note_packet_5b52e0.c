/* Native conversate_action_prep_note_packet_update 0x5b52e0..0x5b53f5. */
#include <stdint.h>

extern uint32_t audio_conversate_prep_note_packet_update_5b44d8(const void *);
extern uint32_t audio_conversate_ui_state_get_5b16d0(void);
extern uint32_t audio_conversate_prep_note_finish_5b476a(void);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_prep_note_packet_update";
static const char null_message[] = "conversate prep note packet data is NULL";
static const char null_short[] = "[conversate]conversate prep note packet data is NULL";
static const char received[] = "prep note packet data received(index: %u, len: %u)";
static const char received_short[] =
    "[conversate]prep note packet data received(index: %u, len: %u)";
static const char failed[] = "prep note packet update failed: index=%u";
static const char failed_short[] =
    "[conversate]prep note packet update failed: index=%u";

uint32_t audio_conversate_action_5b52e0(void *context, const void *arg1,
                                           void *arg2) {
    (void)context;
    (void)arg2;
    if (!arg1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 339u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    const uint8_t *const packet = (const uint8_t *)arg1;
    const uint32_t index = *(const uint32_t *)(const void *)packet;
    const uint16_t length = (uint16_t)((uint16_t)packet[4] | ((uint16_t)packet[5] << 8));
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 345u, received, index, length);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c800000u, received_short, received_short, index, length);
    if (audio_conversate_prep_note_packet_update_5b44d8(packet) != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 349u, failed, index);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, failed_short, failed_short, index);
        return UINT32_MAX;
    }
    if ((uint8_t)audio_conversate_ui_state_get_5b16d0() == 5u &&
        audio_conversate_prep_note_finish_5b476a() != 0u)
        audio_conversate_report_5b02e4(7u, 0u);
    return 0u;
}
