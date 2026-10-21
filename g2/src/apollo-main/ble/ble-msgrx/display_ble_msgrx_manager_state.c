/* Apollo Main compressed SRAM record 0x75d3f4 initializes this observed
 * BLE MsgRx manager at 0x20003ffc. Selected paths use thread/queue cells
 * at +8/+12. Final absolute placement and wider native allocation remain
 * separate gates. */
#include <stdint.h>

_Alignas(4) uint8_t audio_ble_rx_thread_state[16u] = {
    0x69u, 0xeeu, 0x48u, 0x00u, 0x95u, 0xeeu, 0x48u, 0x00u,
    0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u,
};
