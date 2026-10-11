/* Native WsfOsInit 0x52b9b2, called by BLE stack init 0x4b7f64.
 * The 64-byte task state and event handle are BSS, initialized at runtime. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern void *audio_uart_event_dynamic_create(void); /* 0x47ebd8 */
uint8_t audio_wsf_task_state[0x40u]; /* stock RAM 0x20073230 */
void *audio_wsf_event_group; /* stock pointer cell RAM 0x20074ef0 */
void audio_wsf_os_initialize(void) {
    audio_uart_buffer_zero(audio_wsf_task_state,0x40u,0u);
    if(audio_wsf_event_group==0)
        audio_wsf_event_group=audio_uart_event_dynamic_create();
}
