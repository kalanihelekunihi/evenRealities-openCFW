#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native4c8780..4c884a. Saved decoder data/file ownership survives children. */
uint32_t audio_uart_lv_bin_decode_rgb_4c8780(void *decoder,void *descriptor)
{
    (void)decoder;
    volatile uint32_t *d=descriptor;
    volatile uint32_t *data=(volatile uint32_t *)(uintptr_t)d[18];
    void *file=(void *)(uintptr_t)data[0];
    uint32_t cf=d[8]>>8u;
    uint32_t len=(d[9]>>16u)*(uint16_t)d[10];
    if((uint8_t)cf==20u) len+=(d[9]>>16u)*((uint16_t)d[10]/2u);
    uint32_t stride=(uint16_t)d[10];
    void *decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,
        (uint16_t)d[9],d[9]>>16u,(uint8_t)cf,stride);
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    if(decoded==0) {
        audio_uart_lvgl_log(3u,source,800u,"decode_rgb","No memory for rgb file read");
        return 0u;
    }
    void *pixels=(void *)(uintptr_t)((volatile uint32_t *)decoded)[4];
    uint32_t count;
    uint32_t result=audio_uart_lv_fs_read_at_4c8d3c(file,12u,pixels,len,&count);
    if((uint8_t)result!=0u || count!=len) {
        audio_uart_lvgl_log(2u,source,809u,"decode_rgb",
            "Read rgb file failed: %d, with len: %u, expected: %u",(uint32_t)(uint8_t)result,count,len);
        audio_uart_font_bitmap_release(decoded);
        return 0u;
    }
    d[11]=(uint32_t)(uintptr_t)decoded;
    data[7]=(uint32_t)(uintptr_t)decoded;
    return 1u;
}
