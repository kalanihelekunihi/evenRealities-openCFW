/* Native HciDrvHandlerInit 0x4b4a7c; three live handler cells. */
#include <stdint.h>
extern uint8_t audio_ble_hci_driver_handler_id; /* RAM 0x20074fcb */
extern uint8_t audio_ble_hci_driver_rows[0x20]; /* RAM 0x20073e64..0x20073e83 */
void audio_ble_hci_driver_handler_init(uint8_t handler) {
    audio_ble_hci_driver_handler_id=handler;
    audio_ble_hci_driver_rows[0x0cu]=handler;
    audio_ble_hci_driver_rows[0x0au]=2u;
    audio_ble_hci_driver_rows[0x1cu]=handler;
    audio_ble_hci_driver_rows[0x1au]=3u;
}
