/* Native hciTrSendCmd 0x530166. WsfTimerStartSec 0x52a4b8 (audio_ble_hci_timer_start_sec
 * is its alias) lives in ble/ble-smp/display_ble_smp_action_children.c. */
#include <stdint.h>
extern uint32_t audio_ble_hci_driver_write(uint32_t,uint16_t,const void *); /* native 0x4b4a02 */
uint32_t audio_ble_hci_transport_send_cmd(const void *message) {
    const uint8_t *p=(const uint8_t *)message;
    uint16_t length=(uint16_t)((uint16_t)p[2u]+3u);
    return audio_ble_hci_driver_write(1u,length,message)==length;
}
