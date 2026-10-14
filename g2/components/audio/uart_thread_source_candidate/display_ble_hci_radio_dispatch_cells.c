/* Bounded one-byte radio dispatch and mode cells at native Main
 * 0x20074f4f, 0x20074f51, and 0x20074f53. They are tested through the
 * serial, receive, transmit, and platform dispatch paths; exact native
 * SRAM placement and neighboring bytes remain image-linker obligations. */
#include <stdint.h>

volatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f4f;
volatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f51;
volatile uint8_t audio_ble_radio_mode_cell_20074f53;
