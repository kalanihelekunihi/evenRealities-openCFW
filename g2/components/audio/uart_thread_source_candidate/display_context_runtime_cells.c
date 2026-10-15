/* Native display context and locale RAM cells; final placement is gated. */
#include <stdint.h>

volatile uint32_t audio_uart_display_locale_index
    __attribute__((section(".g2_ram_20000030"), aligned(4)));
const void *audio_uart_display_context_list_cell
    __attribute__((section(".g2_ram_200746c8"), aligned(4)));
const void *audio_uart_display_context_active_cell
    __attribute__((section(".g2_ram_200746cc"), aligned(4)));
