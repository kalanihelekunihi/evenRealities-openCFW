/* Native UX_SendBLEStatusReply 0x47d870; eight-byte source template. */
#include <stdint.h>
extern const uint8_t audio_ble_status_message_template[8]; /* ROM 0x78edf4 */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern int32_t audio_ble_send_status_message(uint32_t,const uint8_t *,uint32_t,uint32_t); /* 0x464d1c */
void audio_ble_status_reply(uint8_t ring_mac_ready) {
    uint8_t message[8];
    for(uint32_t i=0;i<8u;i++) message[i]=audio_ble_status_message_template[i];
    message[4]=audio_uart_device_role_get();
    message[5]=audio_uart_device_role_get()==1u?2u:1u;
    message[6]=(ring_mac_ready!=0u)?1u:0u;
    (void)audio_ble_send_status_message(0x103u,message,8u,0u);
}
