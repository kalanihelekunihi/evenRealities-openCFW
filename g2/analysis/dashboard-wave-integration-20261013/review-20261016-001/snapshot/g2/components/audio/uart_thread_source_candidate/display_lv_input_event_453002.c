/* Apollo Main input event dispatch, native 0x453002..0x453051. */
#include <stdint.h>

extern void *audio_uart_lv_basic_box_clear_454746(void *, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_event_list_dispatch_44ffe6(void *, void *, uint32_t);

uint32_t audio_uart_lv_input_event_453002(void *input, uint32_t code, void *target) {
    uint32_t event[7];
    (void)audio_uart_lv_basic_box_clear_454746(event, 0u, sizeof(event));
    event[0] = (uint32_t)(uintptr_t)input;
    event[1] = (uint32_t)(uintptr_t)input;
    event[2] = code;
    event[4] = (uint32_t)(uintptr_t)target;
    void *list = (uint8_t *)input + 0xc0u;
    uint32_t result = (uint8_t)audio_uart_lv_event_list_dispatch_44ffe6(list, event, 1u);
    if ((uint8_t)result == 1u)
        result = (uint8_t)audio_uart_lv_event_list_dispatch_44ffe6(list, event, 0u);
    return (uint8_t)result;
}
