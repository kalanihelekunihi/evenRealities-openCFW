/* Native Conversate disconnect/saved UI route at 0x5b1998. */
#include <stdint.h>

extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint8_t audio_uart_device_role_get(void);
extern void audio_system_alert_close_464c36(uint32_t application_id,
                                            uint32_t payload,
                                            uint32_t length,
                                            uint32_t context);
extern uint32_t audio_uart_page_460084(const char *key);
extern uint32_t audio_uart_page_45fffe(uint32_t fallback, uint32_t index);
extern uint32_t audio_conversate_ui_message_send_58bfb2(uint32_t app_id,
                                                          uint32_t text,
                                                          uint32_t event,
                                                          uint32_t immediate,
                                                          uint32_t timeout);

static const char bluetooth_disconnect[] = "ID_GENERAL_BLUETOOTH_DISCONNECT";
static const char saved[] = "ID_CONVERSATE_SAVED";

uint32_t audio_conversate_ui_route_5b1998(uint32_t state, uint32_t value) {
    if ((uint8_t)state == 3u) {
        if (audio_uart_device_role_get() == 1u)
            audio_system_alert_close_464c36(11u, 0u, 0u, 0u);
        return 0u;
    }
    const char *const key = value == 1u ? bluetooth_disconnect : saved;
    const uint32_t index = audio_uart_page_460084(key);
    const uint32_t text = audio_uart_page_45fffe((uint32_t)(uintptr_t)key,
                                                  index);
    (void)audio_conversate_ui_message_send_58bfb2(
        audio_conversate_ui_app_id_200743a0, text, 11u, 0u,
        value == 1u ? 5000u : 0u);
    return 0u;
}
