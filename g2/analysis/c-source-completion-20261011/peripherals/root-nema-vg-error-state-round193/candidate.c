#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_context_cell; /* authenticated RAM0x20074f04 */
/* Native51564c..51565c: saved context, read-and-clear error word. */
uint32_t audio_uart_nema_vg_get_error_51564c(void) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    uint32_t error=context[32];
    context[32]=0u;
    return error;
}
/* Native51565c..51566c: OR error bits into saved context. */
void audio_uart_nema_vg_set_error_51565c(uint32_t error) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    context[32]=context[32]|error;
}
