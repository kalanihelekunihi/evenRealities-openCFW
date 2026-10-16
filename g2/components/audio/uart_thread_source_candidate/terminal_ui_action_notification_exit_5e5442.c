/* Stock Terminal FSM notification-exit actions 0x5e5442 / 0x5ed748. */
#include <stdint.h>

extern uint32_t audio_terminal_display_queue_handle; /* stock 0x20074a90 */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *);
extern void audio_terminal_fade_out_58c426(uint32_t, uint32_t,
                                           void (*)(void));
extern uint8_t audio_uart_device_role_get(void);
extern void audio_terminal_ui_event_5e5484(uint32_t, uint32_t, uint32_t);
extern void audio_system_alert_close_464c36(uint32_t, uint32_t,
                                             uint32_t, uint32_t);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);

void audio_terminal_ui_finish_5e5420(void) {
    if (audio_uart_device_role_get() == 1u) {
        audio_terminal_ui_event_5e5484(1u, 0u, 0u);
        audio_system_alert_close_464c36(0x30u, 0u, 0u, 0u);
    }
}

int32_t audio_terminal_ui_action_5e5442(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    (void)event_payload;
    uint32_t root = audio_terminal_display_queue_handle;
    if (root == 0u ||
        audio_terminal_ui_object_valid_43e2ea((void *)(uintptr_t)root) == 0u) {
        audio_terminal_ui_finish_5e5420();
    } else {
        audio_terminal_fade_out_58c426(root, 0xfau,
                                        audio_terminal_ui_finish_5e5420);
    }
    return 0;
}

int32_t audio_terminal_ui_action_5ed748(uint32_t old_state,
                                         uint32_t event_payload) {
    (void)old_state;
    (void)event_payload;
    audio_terminal_ui_stop_service_a_5eceb2();
    return audio_terminal_ui_action_5e5442(0x0bu, event_payload);
}
