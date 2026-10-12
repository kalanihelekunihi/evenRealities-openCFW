/* Native HciGetBdAddr 0x530d30; returns live HCI address at RAM 0x200714e0. */
#include <stdint.h>
extern uint8_t audio_ble_hci_local_address[];
uint8_t *HciGetBdAddr(void)
{
    return audio_ble_hci_local_address;
}
