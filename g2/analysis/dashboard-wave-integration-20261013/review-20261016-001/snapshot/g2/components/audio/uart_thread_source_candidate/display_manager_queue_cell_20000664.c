/* Apollo Main display-manager queue handle. Stock view at 0x474066 loads
 * RAM 0x20000658 + 0xc. Placement and runtime initialization need a
 * whole-image layout/startup check. */
#include <stdint.h>

volatile uint32_t audio_uart_display_manager_queue_cell
    __attribute__((section(".g2_ram_20000664"), aligned(4)));
