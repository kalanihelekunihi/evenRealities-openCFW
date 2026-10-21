/* Native ble_param_reset_delayed_event 0x478252. */
#include <stdint.h>

extern void audio_ble_connect_param_request(uint8_t); /* literal 0x47761d */
extern uint32_t audio_event_loop_remove_delayed(void (*)(void)); /* 0x476ace */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t); /* 0x47697e */

void audio_ble_param_reset_delayed_event(uint32_t delay) {
    void (*callback)(void)=(void (*)(void))audio_ble_connect_param_request;
    (void)audio_event_loop_remove_delayed(callback);
    audio_event_loop_push_delayed(callback,0xa4u,delay);
}
