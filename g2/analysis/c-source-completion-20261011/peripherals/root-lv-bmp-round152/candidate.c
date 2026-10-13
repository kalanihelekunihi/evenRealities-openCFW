#include <stdint.h>
extern void *audio_uart_lv_image_decoder_create_4890c8(void);
extern uint32_t audio_uart_lv_bmp_info_4c91e0(void *,void *,void *);
extern uint32_t audio_uart_lv_bmp_open_4c92a8(void *,void *);
extern uint32_t audio_uart_lv_bmp_get_area_4c93a0(void *,void *,const void *,void *);
extern uint32_t audio_uart_lv_fs_file_close_4c6ee0(void *);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_font_bitmap_release(void *);
/* Native 4c94a8..4c94c6; callbacks can mutate descriptor fields. */
void audio_uart_lv_bmp_close_4c94a8(void *decoder,void *descriptor) {
    (void)decoder;
    volatile uint32_t *d=descriptor;
    (void)audio_uart_lv_fs_file_close_4c6ee0((void *)(uintptr_t)d[18]);
    audio_uart_lv_heap_free((void *)(uintptr_t)d[18]);
    if(d[11]!=0u) audio_uart_font_bitmap_release((void *)(uintptr_t)d[11]);
}
/* Native 4c91a8..4c91de is lv_bmp_init, despite legacy assert name. */
void audio_uart_lv_init_assert_4c91a8(void) {
    static const char name[]="BMP";
    volatile uint32_t *d=audio_uart_lv_image_decoder_create_4890c8();
    d[0]=(uint32_t)(uintptr_t)audio_uart_lv_bmp_info_4c91e0;
    d[1]=(uint32_t)(uintptr_t)audio_uart_lv_bmp_open_4c92a8;
    d[2]=(uint32_t)(uintptr_t)audio_uart_lv_bmp_get_area_4c93a0;
    d[3]=(uint32_t)(uintptr_t)audio_uart_lv_bmp_close_4c94a8;
    d[5]=(uint32_t)(uintptr_t)name;
}
