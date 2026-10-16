/* Stock terminal UI teardown 0x5e720c. */
#include <stdint.h>

extern void audio_terminal_ui_stop_voice_5896b4(void);
extern void audio_terminal_ui_stop_timer_5e7ec4(void);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void audio_terminal_ui_stop_service_b_5ec268(void);
extern void audio_terminal_ui_stop_service_c_5ebbc6(void);
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern void audio_terminal_ui_stop_service_e_5ec9c0(void);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern uint32_t audio_terminal_display_queue_handle; /* stock 0x20074a90 */

void audio_terminal_ui_stop_5e720c(void) {
    audio_terminal_ui_stop_voice_5896b4();
    audio_terminal_ui_stop_timer_5e7ec4();
    audio_terminal_ui_stop_service_a_5eceb2();
    audio_terminal_ui_stop_service_b_5ec268();
    audio_terminal_ui_stop_service_c_5ebbc6();
    audio_terminal_ui_stop_service_d_5ec770();
    audio_terminal_ui_stop_service_e_5ec9c0();
    audio_uart_buffer_zero(audio_terminal_ui_state_base, 0x2a0u, 0u);
    audio_terminal_display_queue_handle = 0u;
}
