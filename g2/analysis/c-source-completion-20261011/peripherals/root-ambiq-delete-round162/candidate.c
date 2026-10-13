#include <stdint.h>
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_nema_cl_destroy_5142f0(void *);
extern uint32_t audio_uart_lv_thread_sync_signal_4d4724(void *);
extern void audio_task_delete(void *);
/* Native4d4650..4d465c; taskdelete return discarded. */
uint32_t audio_uart_lv_thread_delete_4d4650(void *thread) {
    audio_task_delete((void *)(uintptr_t)((volatile uint32_t *)thread)[2]);
    return 1u;
}
/* Native4c74f0..4c752e. No VG destroy calls in native configuration. */
int32_t audio_uart_ambiq_delete_4c74f0(void *unit) {
    volatile uint32_t *u=unit;
    audio_uart_font_bitmap_release((void *)(uintptr_t)u[15]);
    if(u[16]!=0u) audio_uart_font_bitmap_release((void *)(uintptr_t)u[16]);
    audio_uart_nema_cl_destroy_5142f0((uint8_t *)unit+144u);
    ((volatile uint8_t *)unit)[57]=1u;
    if(((volatile uint8_t *)unit)[56]!=0u)
        (void)audio_uart_lv_thread_sync_signal_4d4724((uint8_t *)unit+32u);
    return (int32_t)audio_uart_lv_thread_delete_4d4650((uint8_t *)unit+44u);
}
