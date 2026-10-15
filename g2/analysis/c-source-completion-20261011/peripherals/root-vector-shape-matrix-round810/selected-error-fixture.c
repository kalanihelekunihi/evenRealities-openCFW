#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_context_cell;
void audio_uart_nema_vg_set_error_51565c(uint32_t e) {volatile uint8_t *c=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;*(volatile uint32_t *)(c+0x80u)|=e;}
