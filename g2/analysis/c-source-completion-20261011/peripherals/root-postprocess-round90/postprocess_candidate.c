#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);
extern uint32_t audio_uart_lv_draw_buf_adjust_stride_48b34e(void *,uint32_t);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_lv_draw_buf_copy_48ad42(void *,const void *,const void *,const void *);
extern uint32_t audio_uart_lv_color_has_alpha_440fc4(uint32_t);
extern uint32_t audio_uart_lv_draw_buf_has_flag_48b73c(const void *,uint32_t);
extern void audio_uart_lv_draw_buf_premultiply_48b540(void *);
extern void *audio_uart_lv_draw_buf_duplicate_ex_48b134(void *,const void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native489168..48925a; fresh header loads preserve child-call mutations. */
void *audio_uart_lv_decoder_postprocess_489168(void *descriptor,void *decoded)
{
    if(decoded==0) return 0;
    volatile uint8_t *args=(volatile uint8_t *)descriptor+4u;
    volatile uint32_t *buf=decoded;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_image_decoder.c";
    static const char function[]="lv_image_decoder_post_process";
    if(args[0]!=0u && (uint8_t)(buf[0]>>8u)!=20u) {
        uint32_t expected=audio_uart_font_bitmap_stride((uint16_t)buf[1],(uint8_t)(buf[0]>>8u));
        if((uint16_t)buf[2]!=expected && (uint8_t)audio_uart_lv_draw_buf_adjust_stride_48b34e((void *)buf,expected)!=1u) {
            void *aligned=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,(uint16_t)buf[1],buf[1]>>16u,(uint8_t)(buf[0]>>8u),expected);
            if(aligned==0) {audio_uart_lvgl_log(3u,source,258u,function,"No memory for Stride adjust.");return 0;}
            audio_uart_lv_draw_buf_copy_48ad42(aligned,0,(void *)buf,0);buf=aligned;
        }
    }
    if(args[1]!=0u && (uint32_t)((uint8_t)(buf[0]>>8u))-11u>=4u && audio_uart_lv_color_has_alpha_440fc4((uint8_t)(buf[0]>>8u))!=0u && audio_uart_lv_draw_buf_has_flag_48b73c((void *)buf,1u)==0u) {
        if(audio_uart_lv_draw_buf_has_flag_48b73c((void *)buf,32u)==0u) {
            buf=audio_uart_lv_draw_buf_duplicate_ex_48b134(audio_uart_display_lv_root+0x108u,(void *)buf);
            if(buf==0) {audio_uart_lvgl_log(3u,source,282u,function,"No memory for premultiplying.");return 0;}
        }
        audio_uart_lv_draw_buf_premultiply_48b540((void *)buf);
    }
    return (void *)buf;
}
