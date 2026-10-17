/* Native Conversate saved/network-error UI route at 0x5b1a14. */
#include <stdint.h>

extern uint32_t audio_conversate_ui_app_id_200743a0;
extern uint32_t audio_uart_page_460084(const char *key);
extern uint32_t audio_uart_page_45fffe(uint32_t fallback, uint32_t index);
extern uint32_t audio_conversate_ui_message_send_58bfb2(uint32_t app_id,
                                                          uint32_t text,
                                                          uint32_t event,
                                                          uint32_t immediate,
                                                          uint32_t reserved);

static const char network_error[] = "ID_EVEN_AI_NETWORK_ERROR";
static const char saved[] = "ID_CONVERSATE_SAVED";

uint32_t audio_conversate_ui_route_5b1a14(uint32_t state, uint32_t value) {
    (void)state;
    const char *const key = value == 2u ? network_error : saved;
    const uint32_t index = audio_uart_page_460084(key);
    const uint32_t text = audio_uart_page_45fffe((uint32_t)(uintptr_t)key,
                                                  index);
    (void)audio_conversate_ui_message_send_58bfb2(
        audio_conversate_ui_app_id_200743a0, text, 11u, 1u, 0u);
    return 0u;
}
