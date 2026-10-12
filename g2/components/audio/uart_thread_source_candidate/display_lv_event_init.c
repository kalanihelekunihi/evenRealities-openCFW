/* Native LV transition/event initialization 0x4503a4. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[]; /* selected RAM0x2006f548 */
extern void audio_uart_lv_array_init_482b00(uint8_t *,uint32_t);
extern void audio_uart_lv_transition_timer_callback_450758(void *);
extern void *audio_uart_lv_timer_create_464466(void (*)(void *),uint32_t,void *);
extern void audio_uart_lv_transition_schedule_4509da(void); /* selected */

void audio_uart_lv_init_event_4503a4(void)
{
    uint8_t *root=audio_uart_display_lv_root;
    audio_uart_lv_array_init_482b00(root+0xacu,0x60u);
    *(void **)(void *)(root+0xa8u)=
        audio_uart_lv_timer_create_464466(audio_uart_lv_transition_timer_callback_450758,0x10u,0);
    audio_uart_lv_transition_schedule_4509da();
    root[0xa4u]=0u;
    root[0xa5u]=0u;
}
