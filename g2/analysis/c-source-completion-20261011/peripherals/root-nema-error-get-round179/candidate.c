#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[]; /* RAM20074efc */
/* Native4b128a..4b1298: read and clear error on the same saved context. */
uint32_t audio_uart_nema_get_error_4b128a(void) {
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    uint32_t error=context[8];
    context[8]=0u;
    return error;
}
