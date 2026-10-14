/* Two authenticated Apollo Main radio ROM strings; experimental placement. */
#include <stdint.h>

/* Stock 0x75d590; 32 bytes including NUL. */
const uint8_t audio_ble_hci_radio_command_error_75d590[] = "write data fail, status: 0x%x\r\n";
_Static_assert(sizeof(audio_ble_hci_radio_command_error_75d590) == 32u, "size");

/* Stock 0x77d90c; 20 bytes including NUL. */
const uint8_t audio_ble_hci_radio_resource_log5_77d90c[] = "Trim force update\r\n";
_Static_assert(sizeof(audio_ble_hci_radio_resource_log5_77d90c) == 20u, "size");
