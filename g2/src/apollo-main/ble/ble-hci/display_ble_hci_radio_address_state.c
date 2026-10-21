/* Bounded six-byte radio address/identifier state at native Main
 * 0x20074148. Custom BD address and radio boot driver state are two names
 * for the same observed bytes. Native allocation extent beyond byte 5 and
 * absolute SRAM placement remain image-level gates. */
#include <stdint.h>

uint8_t audio_ble_custom_bd_address[6u];
extern uint8_t audio_ble_hci_radio_driver_state[6u]
    __attribute__((alias("audio_ble_custom_bd_address")));
