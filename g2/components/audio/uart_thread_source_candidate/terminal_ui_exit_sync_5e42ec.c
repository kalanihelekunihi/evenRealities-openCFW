/* Stock terminal_display_exit_sync 0x5e42ec. */
#include <stdint.h>

extern uint8_t audio_terminal_mode_sync_pending; /* stock 0x2006e344 */
extern uint32_t audio_settings_terminal_mode(void); /* stock 0x46c630 */
extern uint32_t audio_terminal_send_status_reply(const void *); /* stock 0x5ceba2 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);

void audio_terminal_ui_exit_sync_5e42ec(void) {
    uint8_t reply[8];
    audio_uart_buffer_zero(reply, 2u, 0u);
    if (audio_terminal_mode_sync_pending != 0u) {
        audio_terminal_mode_sync_pending = 0u;
        reply[0] = (uint8_t)(audio_settings_terminal_mode() == 0u ? 1u : 2u);
        (void)audio_terminal_send_status_reply(reply);
    }
}
