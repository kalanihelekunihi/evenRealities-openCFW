/* Native display-buffer preparation 0x473928 and lock setup 0x4738a8.
 * The display object allocator/driver body 0x473782 remains a real child. */
#include <stdint.h>

extern void *audio_uart_display_lock; /* *DAT_0047390c */
extern const char *audio_uart_display_source_path; /* DAT_004738f0 */
extern const char audio_uart_display_lock_function[]; /* PTR_s_display_buffer_lock_init_00473924 */
extern void *audio_queue_create_dynamic(uint32_t,uint32_t,uint32_t); /* selected 0x441636 */
extern uint32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t); /* 0x4417ee */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...); /* 0x44d25c */
extern void audio_uart_display_driver_create(void); /* 0x473782 */

void audio_uart_display_lock_init(void) {
    audio_uart_display_lock=audio_queue_create_dynamic(1u,0u,3u);
    if(audio_uart_display_lock==0)
        audio_uart_lvgl_log(3u,audio_uart_display_source_path,0x140u,
                            audio_uart_display_lock_function);
    (void)audio_uart_queue_send(audio_uart_display_lock,0,0u,0u);
}

void audio_uart_display_clock_finish(void) {
    audio_uart_display_lock_init();
    audio_uart_display_driver_create();
}
