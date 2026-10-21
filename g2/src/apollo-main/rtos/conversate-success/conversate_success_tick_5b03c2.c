/* Native Conversate success timestamp helper 0x5b03c2..0x5b03d7. */
#include <stdint.h>
extern uint8_t audio_uart_device_role_get(void); /* native 0x45a568 */
extern uint32_t g2_flashdb_candidate_tick(void); /* native 0x4490cc */
extern uint32_t audio_conversate_last_success_tick_20074394;

void audio_conversate_success_5b03c2(void) {
    if (audio_uart_device_role_get() == 1u)
        audio_conversate_last_success_tick_20074394 =
            g2_flashdb_candidate_tick();
}
