/* Native WsfTimerStartSec 0x52a4b8 and hciTrSendCmd 0x530166. */
#include <stdint.h>
extern void audio_ble_wsf_timer_insert(void *,uint32_t); /* native 0x52a424 */
extern uint32_t audio_ble_hci_driver_write(uint32_t,uint16_t,const void *); /* native 0x4b4a02 */
void audio_ble_hci_timer_start_sec(void *timer,uint32_t seconds) {
    audio_ble_wsf_timer_insert(timer,seconds*100u);
}
uint32_t audio_ble_hci_transport_send_cmd(const void *message) {
    const uint8_t *p=(const uint8_t *)message;
    uint16_t length=(uint16_t)((uint16_t)p[2u]+3u);
    return audio_ble_hci_driver_write(1u,length,message)==length;
}
