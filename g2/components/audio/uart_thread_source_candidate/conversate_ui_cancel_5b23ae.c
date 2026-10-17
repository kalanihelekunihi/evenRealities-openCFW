/* Native Conversate UI minute update 0x5b23ae..0x5b23e3. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_quicklist_tick_now(void);
extern uint8_t audio_conversate_ui_deinit_tail_200713fd[];
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);

void audio_conversate_ui_cancel_5b23ae(void) {
    if (audio_uart_device_role_get() != 1u)
        return;
    uint32_t *const minutes =
        (uint32_t *)(void *)(audio_conversate_ui_deinit_tail_200713fd + 7u);
    if (*minutes == 0u)
        return;
    uint32_t seconds = audio_quicklist_tick_now();
    uint32_t next_minutes = seconds / 60u;
    if (next_minutes == *minutes)
        return;
    *minutes = next_minutes;
    audio_conversate_report_5b02e4(17u, seconds);
}
