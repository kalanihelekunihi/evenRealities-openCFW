/* Handler byte and two observed 0x10-byte WSF timer slices. */
#include <stdint.h>

volatile uint8_t audio_ble_hci_driver_handler_id
    __attribute__((section(".g2_ram_20074fcb")));
uint8_t audio_ble_hci_radio_timer[0x10u]
    __attribute__((section(".g2_ram_20073e64")));
uint8_t audio_ble_hci_driver_secondary_timer[0x10u]
    __attribute__((section(".g2_ram_20073e74")));
