/* Native hciCmdTimeout 0x52aee6 and DmDevReset 0x4b3026. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[]; /* live 0x20073b78 */
extern void *audio_wsf_msg_alloc(uint16_t); /* selected 0x4bf99e */
extern void audio_wsf_msg_send(uint8_t,void *); /* selected 0x4bf9ba */
extern void audio_ble_hci_driver_radio_shutdown(void); /* 0x4b49ce */
extern void audio_ble_hci_driver_radio_boot(uint8_t); /* 0x4b48a6 */

extern void audio_ble_dm_device_reset(void); /* opencfw U5: now provided by the Cordio unit */
void audio_ble_hci_command_timeout(void *event) {
    (void)event;
    audio_ble_hci_driver_radio_shutdown();
    audio_ble_hci_driver_radio_boot(0u);
    audio_ble_dm_device_reset();
}
