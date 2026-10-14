/* Apollo Main compressed SRAM record 0x75d3f4 initializes the mutable
 * display-thread wait word at 0x20000654 to UINT32_MAX. The display thread
 * later shortens and restores it; absolute RAM placement remains a gate. */
#include <stdint.h>

uint32_t audio_uart_display_wait = UINT32_MAX;
