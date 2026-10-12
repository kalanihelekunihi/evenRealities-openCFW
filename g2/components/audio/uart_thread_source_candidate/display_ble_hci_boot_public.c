/* Native HciDrvRadioBoot 0x4b48a6 already reduced as
 * audio_ble_hci_driver_radio_boot, verified by five connected native/C cases. */
#include <stdint.h>
extern uint32_t audio_ble_hci_driver_radio_boot(uint8_t);
uint32_t HciDrvRadioBoot(uint8_t with_identifier) {
    return audio_ble_hci_driver_radio_boot(with_identifier);
}
