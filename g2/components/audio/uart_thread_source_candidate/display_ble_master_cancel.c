/* Native central_cancel_connect_retry_work 0x4a17f4 and event forwarder 0x4a153c. */
#include <stdint.h>
extern volatile uint8_t audio_ble_master_connect_state; /* RAM 0x20074f87 */
extern void audio_ble_master_connect_event(void); /* native 0x4a1b60 */
extern uint32_t audio_event_loop_remove_delayed(void (*)(void)); /* 0x476ace */
extern void audio_ble_master_emit_ring_event(uint8_t); /* native 0x4ac16c */
void audio_ble_master_ring_link_event(uint8_t event) { /* 0x4a153c */
    audio_ble_master_emit_ring_event(event);
}
void audio_ble_master_cancel_retry(void) { /* 0x4a17f4 */
    if(audio_ble_master_connect_state==1u) audio_ble_master_ring_link_event(6u);
    audio_ble_master_connect_state=0u;
    (void)audio_event_loop_remove_delayed(audio_ble_master_connect_event);
}
