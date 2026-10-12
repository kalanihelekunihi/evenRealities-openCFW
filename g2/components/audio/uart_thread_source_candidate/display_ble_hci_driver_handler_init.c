/* Native HciDrvHandlerInit 0x4b4a7c. The two timer objects remain live RAM. */
#include <stdint.h>

extern volatile uint8_t audio_ble_hci_driver_handler_id; /* 0x20074fcb */
extern uint8_t audio_ble_hci_radio_timer[]; /* 0x20073e64 */
extern uint8_t audio_ble_hci_driver_secondary_timer[]; /* 0x20073e74 */

void audio_ble_hci_driver_handler_init(uint8_t handler)
{
    audio_ble_hci_driver_handler_id = handler;
    audio_ble_hci_radio_timer[0x0cu] = handler;
    audio_ble_hci_radio_timer[0x0au] = 2u;
    audio_ble_hci_driver_secondary_timer[0x0cu] = handler;
    audio_ble_hci_driver_secondary_timer[0x0au] = 3u;
}
