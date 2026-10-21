/* Native conversate_action_prep_note_list_update 0x5b5150..0x5b52c9. */
#include <stdint.h>

extern void audio_conversate_prep_note_list_update_5b4378(const void *);
extern uint32_t audio_conversate_ui_state_get_5b16d0(void);
extern uint32_t audio_uart_device_role_get(void);
extern uint32_t audio_system_alert_command_45a8ee(uint32_t, uint32_t,
                                                   uint32_t, uint32_t);
extern void audio_conversate_enter_loading_5b57ac(void);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_prep_note_list_update";
static const char null_message[] = "conversate prep note list data is NULL";
static const char null_short[] = "[conversate]conversate prep note list data is NULL";
static const char received[] = "prep note list data received(count: %d, first: %s)";
static const char received_short[] =
    "[conversate]prep note list data received(count: %d, first: %s)";
static const char empty[] = "prep note list data received(count: 0)";
static const char empty_short[] = "[conversate]prep note list data received(count: 0)";
static const char skip[] = "prep note list empty, skip & start and enter loading directly";
static const char skip_short[] =
    "[conversate]prep note list empty, skip & start and enter loading directly";

uint32_t audio_conversate_action_5b5150(void *context, const void *arg1,
                                           void *arg2) {
    (void)context;
    (void)arg2;
    if (!arg1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 300u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    const uint8_t *const packet = (const uint8_t *)arg1;
    const uint16_t count = (uint16_t)((uint16_t)packet[0] | ((uint16_t)packet[1] << 8));
    if (count != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 304u, received,
                               count, packet + 10);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x0c800000u, received_short, received_short,
                             count, packet + 10);
    } else {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 306u, empty);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x0c000000u, empty_short, empty_short);
    }
    audio_conversate_prep_note_list_update_5b4378(arg1);
    const uint8_t state = (uint8_t)audio_conversate_ui_state_get_5b16d0();
    if (state == 0u) {
        if (audio_uart_device_role_get() == 1u)
            (void)audio_system_alert_command_45a8ee(11u, 0u, 0u, 500u);
    } else if (count == 0u && state == 3u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 319u, skip);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x0c000000u, skip_short, skip_short);
        audio_conversate_enter_loading_5b57ac();
        audio_conversate_report_5b02e4(12u, 0u);
    } else {
        audio_conversate_report_5b02e4(2u, 0u);
    }
    return 0u;
}
