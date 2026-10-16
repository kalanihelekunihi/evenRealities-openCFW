/* Stock Main 0x478110: reset BLE connection parameter timer for a pull. */
#include <stdint.h>
extern volatile uint8_t audio_ble_current_conn_mode;
extern void audio_ble_connect_param_request(uint8_t);
extern uint32_t audio_event_loop_remove_delayed(void (*)(void));
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);

volatile uint8_t audio_tracepoint_pull_connection_flag_20074f8f
    __attribute__((section(".bss.opencfw.tracepoint.pull_connection_flag"),used));

void audio_tracepoint_reset_pull_478110(uint8_t delayed) {
    void (*callback)(void)=(void (*)(void))audio_ble_connect_param_request;
    if(audio_tracepoint_pull_connection_flag_20074f8f!=0u)
        audio_ble_current_conn_mode=0xa4u;
    (void)audio_event_loop_remove_delayed(callback);
    if(delayed!=0u)
        audio_event_loop_push_delayed(callback,0xa4u,60000u);
    audio_event_loop_push_delayed(callback,0xa3u,0u);
}
