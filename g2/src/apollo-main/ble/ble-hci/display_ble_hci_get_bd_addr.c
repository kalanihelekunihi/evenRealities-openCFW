/* Native HciGetBdAddr 0x530d30; returns live HCI address at RAM 0x200714e0. */
#include <stdint.h>
extern uint8_t audio_ble_hci_controller_state_20071478[];
uint8_t *HciGetBdAddr(void)
{
    return audio_ble_hci_controller_state_20071478+0x68u;
}
