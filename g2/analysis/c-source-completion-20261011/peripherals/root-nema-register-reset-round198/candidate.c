#include <stdint.h>
extern volatile uint32_t audio_uart_nema_last_submission; /* authenticated RAM20002e08 */
extern const uint32_t audio_uart_nema_register_base; /* authenticated flash78f2f4 */
/* Native514184..514194. */
void audio_uart_nema_reset_last_submission_514184(void) { audio_uart_nema_last_submission=UINT32_MAX; }
uint32_t audio_uart_nema_last_submission_51418e(void) { return audio_uart_nema_last_submission; }
/* Native51403c..514050. Wrapped byte-offset register access. */
uint32_t audio_uart_nema_reg_read_51403c(uint32_t offset) {
    return *(volatile uint32_t *)(uintptr_t)(audio_uart_nema_register_base+offset);
}
void audio_uart_nema_reg_write_514046(uint32_t offset,uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)(audio_uart_nema_register_base+offset)=value;
}
