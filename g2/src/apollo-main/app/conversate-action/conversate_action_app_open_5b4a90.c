/* Native conversate_action_app_open 0x5b4a90..0x5b4cc7. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern uint32_t audio_conversate_ui_state_get_5b16d0(void);
extern const char *audio_conversate_ui_state_name_5b16dc(uint32_t);
extern uint8_t audio_conversate_machine_context_200e3aec;
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern void audio_conversate_apply_config_5b133c(void);
extern void audio_conversate_page_show_54f380(uint32_t);
extern void audio_conversate_prep_note_update_5b43ee(const void *);
extern void audio_conversate_tag_storage_init_59619e(void);
extern uint32_t audio_uart_device_role_get(void);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t, uint32_t, const void *);
extern uint32_t audio_system_alert_command_45a8ee(uint32_t, uint32_t,
                                                    uint32_t, uint32_t);
extern uint32_t audio_quicklist_tick_now(void);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_app_open";
static const char null_message[] = "pData is NULL";
static const char null_short[] = "[conversate]pData is NULL";
static const char invalid_message[] =
    "conversate ui state is invalid, no need to start: [%d|%s]";
static const char invalid_short[] =
    "[conversate]conversate ui state is invalid, no need to start: [%d|%s]";
static const char config_message[] =
    "ai cue: %d, transcribe: %d, auto_pop_en: %d, use_audio: %d, cue_duration: %d";
static const char config_short[] =
    "[conversate]ai cue: %d, transcribe: %d, auto_pop_en: %d, use_audio: %d, cue_duration: %d";
static const char prep_message[] = "prep note data updated: %s, total_packets=%u";
static const char prep_short[] =
    "[conversate]prep note data updated: %s, total_packets=%u";
static const uint32_t wear_descriptor[2] = {1u, 2u};

uint32_t audio_conversate_action_5b4a90(void *context, const void *arg1,
                                           void *arg2) {
    (void)arg2;
    if (!arg1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 125u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    const uint8_t state = (uint8_t)audio_conversate_ui_state_get_5b16d0();
    if (state != 0u && state != 1u && state != 3u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 132u, invalid_message,
                               state, audio_conversate_ui_state_name_5b16dc(state));
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04800000u, invalid_short, invalid_short,
                             state, audio_conversate_ui_state_name_5b16dc(state));
        return UINT32_MAX;
    }
    uint8_t *const ctx = (uint8_t *)context;
    const uint8_t *const packet = (const uint8_t *)arg1;
    audio_conversate_machine_context_200e3aec = 1u;
    if (packet[1] != 0u) {
        (void)audio_queue_copy_bytes(ctx + 1, packet + 2, 5u);
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 141u, config_message,
                               ctx[1], ctx[2], ctx[3], ctx[4], ctx[5]);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x0d400000u, config_short, config_short,
                             ctx[1], ctx[2], ctx[3], ctx[4], ctx[5]);
        audio_conversate_apply_config_5b133c();
        if (ctx[4] != 0u)
            audio_conversate_page_show_54f380(4u);
    }
    if (packet[7] != 0u) {
        audio_conversate_prep_note_update_5b43ee(packet + 8);
        const uint32_t total_packets = (uint32_t)packet[0x8c] |
            ((uint32_t)packet[0x8d] << 8) |
            ((uint32_t)packet[0x8e] << 16) |
            ((uint32_t)packet[0x8f] << 24);
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 153u, prep_message,
                               packet + 10, total_packets);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x10800000u, prep_short, prep_short,
                             packet + 10, total_packets);
    }
    audio_conversate_tag_storage_init_59619e();
    if (state == 0u) {
        if (audio_uart_device_role_get() == 1u)
            audio_uart_ring_wear_persist_48eb32(0x40101u, 2u, wear_descriptor);
        if (audio_uart_device_role_get() == 1u)
            (void)audio_system_alert_command_45a8ee(11u, 0u, 0u, 500u);
    } else if (state == 1u) {
        audio_conversate_report_5b02e4(4u, audio_quicklist_tick_now());
    } else {
        audio_conversate_report_5b02e4(3u, 0u);
    }
    return 0u;
}
