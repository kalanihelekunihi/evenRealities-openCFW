/* Apollo Main compressed SRAM record 0x75d3f4 initializes these mutable
 * cells at 0x20000064 and 0x20004526. Their native addresses still need
 * final scatter placement; adjacent initialized bytes are not claimed. */
#include <stdint.h>

uint32_t audio_uart_display_page_size_cell = 0x400u;
volatile uint16_t audio_uart_hub_role_cell = 3u;
