/* Cordio HciGetMaxRxAclLen at stock Main 0x530d4c. */
#include <stdint.h>

extern uint8_t audio_ble_hci_controller_state_20071478[];

uint16_t audio_ble_hci_max_rx_acl_len_530d4c(void)
{
    return (uint16_t)audio_ble_hci_controller_state_20071478[0x7cu] |
           ((uint16_t)audio_ble_hci_controller_state_20071478[0x7du] << 8);
}
