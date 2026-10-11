/* Native ring-link event emission 0x4ac16c. */
#include <stdint.h>
extern const uint8_t audio_ble_master_ring_event_template[8]; /* ROM 0x78e4fc */
extern uint32_t audio_uart_command_pending(void); /* productModeGet 0x4abe60 */
extern void audio_ble_device_manager_send(const uint8_t *); /* 0x4c659a */
void audio_ble_master_emit_ring_event(uint8_t event) {
    if(audio_uart_command_pending()==1u) return;
    uint8_t message[8];
    for(uint32_t i=0;i<8u;i++) message[i]=audio_ble_master_ring_event_template[i];
    message[0]=3u;message[1]=0u;
    message[2]=1u;message[3]=0u;
    message[4]=event;
    audio_ble_device_manager_send(message);
}
