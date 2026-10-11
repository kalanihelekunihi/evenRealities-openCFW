/* Native hciCmdTimeout 0x52aee6 and DmDevReset 0x4b3026. */
#include <stdint.h>
extern uint8_t audio_ble_dm_handler_state[]; /* live 0x20073b78 */
extern void *audio_wsf_msg_alloc(uint16_t); /* selected 0x4bf99e */
extern void audio_wsf_msg_send(uint8_t,void *); /* selected 0x4bf9ba */
extern void audio_ble_hci_driver_radio_shutdown(void); /* 0x4b49ce */
extern void audio_ble_hci_driver_radio_boot(uint8_t); /* 0x4b48a6 */

void audio_ble_dm_device_reset(void) {
    uint8_t *state=audio_ble_dm_handler_state;
    if(state[0x10u]!=0u)state[0x10u]=0u;
    uint8_t *message=(uint8_t *)audio_wsf_msg_alloc(4u);
    if(message!=0) {
        message[2]=0x38u;
        audio_wsf_msg_send(state[0xcu],message);
    }
}
void audio_ble_hci_command_timeout(void *event) {
    (void)event;
    audio_ble_hci_driver_radio_shutdown();
    audio_ble_hci_driver_radio_boot(0u);
    audio_ble_dm_device_reset();
}
