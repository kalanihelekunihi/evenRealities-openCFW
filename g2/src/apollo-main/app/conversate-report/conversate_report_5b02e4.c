/* Native Conversate display report 0x5b02e4..0x5b03c1. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t);
extern const char *audio_conversate_ui_event_name_5b16fc(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_uart_master_display_refresh(uint32_t, const void *,
                                              uint16_t, uint32_t);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate.c";
static const char function[] = "conversate_request_display";
static const char sent[] = "conversate request reflash, event: %d|%s, value: %d";
static const char sent_short[] =
    "[conversate]conversate request reflash, event: %d|%s, value: %d";
static const char skipped[] = "conversate is not running, ignore reflash request";
static const char skipped_short[] =
    "[conversate]conversate is not running, ignore reflash request";

void audio_conversate_report_5b02e4(uint32_t event, uint32_t value) {
    if (audio_uart_device_role_get() != 1u)
        return;
    struct {
        uint8_t event;
        uint8_t unspecified_padding[3];
        uint32_t value;
    } packet;
    packet.event = (uint8_t)event;
    packet.value = value;
    if (audio_quicklist_refresh_enabled_4434d0(11u) == 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 126u, sent,
                               (uint8_t)event,
                               audio_conversate_ui_event_name_5b16fc((uint8_t)event), value);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x0cc00000u, sent_short, sent_short,
                             (uint8_t)event,
                             audio_conversate_ui_event_name_5b16fc((uint8_t)event), value);
        audio_uart_master_display_refresh(11u, &packet, 8u, 0u);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, path, function, 130u, skipped);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x08000000u, skipped_short, skipped_short);
}
