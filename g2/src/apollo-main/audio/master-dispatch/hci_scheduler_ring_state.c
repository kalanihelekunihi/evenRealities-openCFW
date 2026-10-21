/* Six-word HCI scheduler ring control structure at native RAM 0x20073ba8. */
#include <stdint.h>

uint8_t audio_ble_hci_radio_scheduler_state[24u]
    __attribute__((section(".g2_ram_20073ba8")));
