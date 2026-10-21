/* Provisional nanopb Case RX frame at stock RAM 0x200f5a90..99.
 * The TX frame begins at 0x200f5a9c; final layout and startup remain gated.
 */
#include <stdint.h>
uint8_t audio_uart_case_rx_frame_200f5a90[10]
    __attribute__((section(".g2_ram_200f5a90"),used));
