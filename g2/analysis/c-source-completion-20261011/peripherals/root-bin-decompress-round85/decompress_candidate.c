#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_bin_decoder_data_get_4c81a2(void *);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native4c8d8c..4c8e78. RLE/LZ4 are disabled in the locked native build;
 * these are native diagnostic/cleanup branches, not substitute codec stubs. */
uint32_t audio_uart_lv_bin_decompress_image_4c8d8c(void *descriptor,void *compressed)
{
    volatile uint32_t *d=descriptor,*c=compressed;
    if(audio_uart_lv_bin_decoder_data_get_4c81a2(descriptor)==0) return 0u;
    uint32_t out_len=c[2],input_len=c[1];
    uint32_t stride=(uint16_t)d[10];
    void *decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,(uint16_t)d[9],d[9]>>16u,(uint8_t)(d[8]>>8u),stride);
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    static const char function[]="decompress_image";
    if(decoded==0) {
        audio_uart_lvgl_log(2u,source,1117u,function,"No memory for decompressed image, input: %u, output: %u",input_len,out_len);return 0u;
    }
    if(((volatile uint32_t *)decoded)[3]<out_len) {
        audio_uart_lvgl_log(3u,source,1122u,function,"Decompressed size mismatch: %u > %u",out_len,((volatile uint32_t *)decoded)[3]);
        audio_uart_font_bitmap_release(decoded);return 0u;
    }
    (void)((volatile uint32_t *)decoded)[4];
    if((((volatile uint8_t *)compressed)[0]&15u)==1u)
        audio_uart_lvgl_log(2u,source,1147u,function,"RLE decompress is not enabled");
    else if((((volatile uint8_t *)compressed)[0]&15u)==2u)
        audio_uart_lvgl_log(2u,source,1164u,function,"LZ4 decompress is not enabled");
    else audio_uart_lvgl_log(2u,source,1171u,function,"Unknown compression method: %d",(uint32_t)(((volatile uint8_t *)compressed)[0]&15u));
    audio_uart_font_bitmap_release(decoded);return 0u;
}
