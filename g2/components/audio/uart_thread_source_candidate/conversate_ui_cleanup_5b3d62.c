/* Native Conversate UI exit cleanup 0x5b3d62..0x5b3d85. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t g2_flashdb_candidate_tick(void);
extern void audio_conversate_ui_cleanup_child_5b38ee(uint32_t);
extern void audio_conversate_ui_cleanup_flush_5b39b4(uint32_t);
extern void audio_conversate_ui_cleanup_commit_5b3a88(uint32_t);

void audio_conversate_ui_cleanup_5b3d62(void) {
    if (audio_uart_device_role_get() == 1u) {
        uint32_t tick = g2_flashdb_candidate_tick();
        audio_conversate_ui_cleanup_child_5b38ee(tick);
        audio_conversate_ui_cleanup_flush_5b39b4(tick);
        audio_conversate_ui_cleanup_commit_5b3a88(tick);
    }
}
