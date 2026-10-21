/* Native conversate_ui_send_start_request 0x5b57ac..0x5b5885. */
#include <stdint.h>

extern uint8_t audio_conversate_reply_status_200d6b84[];
extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_conversate_start_request_5b1f2e(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_menu_page.c";
static const char function[] = "conversate_ui_send_start_request";
static const char skip_message[] = "send start request: skip and start";
static const char skip_short[] =
    "[conversate.ui]send start request: skip and start";
static const char selected_message[] =
    "send start request: prep note id=%d index=%d";
static const char selected_short[] =
    "[conversate.ui]send start request: prep note id=%d index=%d";

static uint16_t half(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

void audio_conversate_enter_loading_5b57ac(void) {
    const uint8_t *const list = audio_conversate_reply_status_200d6b84 + 4u;
    uint32_t index = word(audio_conversate_ui_settings_extension_20071369 + 0x83u);
    if (index == UINT32_MAX || half(list) == 0u) {
        (void)audio_conversate_start_request_5b1f2e(1u, 0u);
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 52u, skip_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x0c000000u, skip_short, skip_short);
        return;
    }
    uint32_t identifier = word(list + 0x88u * index + 4u);
    (void)audio_conversate_start_request_5b1f2e(0u, identifier);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 56u, selected_message,
                           identifier, index);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c800000u, selected_short, selected_short,
                         identifier, index);
}
