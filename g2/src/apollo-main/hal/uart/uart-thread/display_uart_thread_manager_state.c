/* Apollo Main compressed SRAM record 0x75d3f4 initializes this observed
 * UART thread-manager span at 0x200040d8; the next thread record begins at
 * 0x200040fc. The selected ring-sync path reads its handle at offset 28.
 * Absolute placement and complete native structure ownership remain gates. */
#include <stdint.h>

_Alignas(4) uint8_t audio_uart_thread_manager_state[36u] = {
    0x49u, 0x9bu, 0x4cu, 0x00u, 0x71u, 0x9bu, 0x4cu, 0x00u,
};
