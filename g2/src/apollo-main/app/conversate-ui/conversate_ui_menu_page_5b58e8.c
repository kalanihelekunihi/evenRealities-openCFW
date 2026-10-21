/* Native Conversate display-menu-page action, 0x5b58e8..0x5b59f9. */
#include <stdint.h>

extern uint8_t audio_ux_get_system_ble_status(void);
extern uint8_t audio_conversate_ui_settings_extension_20071369[];
extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint32_t audio_uart_page_460084(const char *);
extern uint32_t audio_uart_page_45fffe(const char *, uint32_t);
extern uint32_t audio_conversate_ui_message_send_58bfb2(uint32_t, uint32_t,
                                                          uint32_t, uint32_t,
                                                          uint32_t);
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_conversate_menu_style_5b5720(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_conversate_menu_request_prep_notes_5b1e52(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.ui";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_menu_page.c";
static const char function[] = "conversate_ui_action_display_menu_page";
static const char disconnected[] = "BLE disconnected, show exit prompt";
static const char disconnected_short[] =
    "[conversate.ui]BLE disconnected, show exit prompt";
static const char request[] = "request prep note list";
static const char request_short[] = "[conversate.ui]request prep note list";
static const char disconnect_key[] = "ID_GENERAL_BLUETOOTH_DISCONNECT";

uint32_t audio_conversate_ui_route_5b58e8(uint32_t state, uint32_t value) {
    (void)state;
    (void)value;
    if (audio_ux_get_system_ble_status() == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, source, function, 0x62u,
                               disconnected);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, disconnected_short,
                                        disconnected_short);
        const uint32_t length = audio_uart_page_460084(disconnect_key);
        const uint32_t text = audio_uart_page_45fffe(disconnect_key, length);
        (void)audio_conversate_ui_message_send_58bfb2(
            audio_conversate_ui_app_id_200743a0, text, 11u, 0u, 0x1388u);
        return UINT32_MAX;
    }

    volatile uint8_t *const ui = (volatile uint8_t *)(uintptr_t)
        ((uintptr_t)audio_conversate_ui_settings_extension_20071369 - 1u);
    const uint32_t root = audio_uart_page_43de82(audio_conversate_ui_app_id_200743a0);
    *(volatile uint32_t *)(void *)(ui + 4u) = root;
    audio_uart_page_43f4c0(root, 0x240u, 0x120u);
    audio_uart_page_43f09a(root, 0u, 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44146a(root, 0u, 0u);
    audio_conversate_menu_style_5b5720(root, 0u, 0u);
    audio_uart_page_43dfa4(root, 0x10u);
    audio_conversate_menu_request_prep_notes_5b1e52();
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, source, function, 0x71u, request);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c000000u, request_short, request_short);
    return 0u;
}
