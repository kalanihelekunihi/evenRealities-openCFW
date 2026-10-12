#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_read_at_4c8d3c(void *,uint32_t,void *,uint32_t,uint32_t *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void audio_uart_font_bitmap_release(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static uint32_t alpha_lsl(uint32_t value,uint32_t shift)
{
    uint32_t amount=(uint8_t)shift;
    return amount>=32u?0u:value<<amount;
}
/* Full native4c884a..4c887c; byte-valued interpolation, native register shifts. */
uint32_t audio_uart_lv_bin_bit_extend_4c884a(uint32_t value,uint32_t bpp)
{
    if((uint8_t)value==0u) return 0u;
    uint32_t result=value,position=bpp;
    while((uint8_t)position<8u) {
        result|=alpha_lsl((uint8_t)value,8u-position);
        position+=bpp;
    }
    return (uint8_t)result;
}
/* Full native4c887c..4c8a10; literal pool beginning4c8a10 excluded. */
uint32_t audio_uart_lv_bin_decode_alpha_4c887c(void *decoder,void *descriptor)
{
    (void)decoder;
    volatile uint32_t *d=descriptor;
    volatile uint32_t *data=(volatile uint32_t *)(uintptr_t)d[18];
    uint32_t bits=audio_uart_lv_color_bpp_440f44((uint8_t)(d[8]>>8u));
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c";
    if((uint8_t)bits==0u) {
        audio_uart_lvgl_log(3u,source,846u,"decode_alpha_only","Error color format: %d",(uint32_t)(uint8_t)(d[8]>>8u));
        return 0u;
    }
    uint32_t row=((uint32_t)(uint16_t)d[10]*8u)/(uint8_t)bits;
    uint32_t out_stride=(row*8u+7u)>>3u;
    uint32_t out_len=row*(d[9]>>16u);
    uint32_t file_len=(uint32_t)(uint16_t)d[10]*(d[9]>>16u);
    void *decoded=audio_uart_lv_draw_buf_create_ex_48b010(audio_uart_display_lv_root+0x108u,
        (uint16_t)d[9],d[9]>>16u,14u,out_stride);
    if(decoded==0) {
        audio_uart_lvgl_log(3u,source,859u,"decode_alpha_only","Out of memory");
        return 0u;
    }
    uintptr_t pixels=((volatile uint32_t *)decoded)[4];
    if((d[8]&0x00080000u)!=0u) {
        void *decompressed=(void *)(uintptr_t)data[8];
        audio_uart_lv_grid_copy_454738((void *)pixels,(void *)(uintptr_t)((volatile uint32_t *)decompressed)[4],file_len);
    } else if(((volatile uint8_t *)descriptor)[16]==1u) {
        uint32_t count;
        uint32_t result=audio_uart_lv_fs_read_at_4c8d3c((void *)(uintptr_t)data[0],12u,(void *)pixels,file_len,&count);
        if((uint8_t)result!=0u || count!=file_len) {
            audio_uart_lvgl_log(2u,source,872u,"decode_alpha_only",
                "Read header failed: %d, with len: %u, expected: %u",(uint32_t)(uint8_t)result,count,file_len);
            audio_uart_font_bitmap_release(decoded);
            return 0u;
        }
    } else if(((volatile uint8_t *)descriptor)[16]==0u) {
        void *image=(void *)(uintptr_t)d[3];
        audio_uart_lv_grid_copy_454738((void *)pixels,(void *)(uintptr_t)((volatile uint32_t *)image)[4],file_len);
    }
    if((uint8_t)(d[8]>>8u)!=14u) {
        uintptr_t input=pixels+file_len-1u,output=pixels+out_len-1u;
        uint32_t mask=alpha_lsl(1u,bits)-1u,shift=0u;
        for(uint32_t i=0u;i<out_len;++i) {
            uint32_t amount=(uint8_t)shift;
            uint32_t value=amount>=32u?0u:*(uint8_t *)input>>amount;
            value&=mask;
            *(uint8_t *)output=(uint8_t)audio_uart_lv_bin_bit_extend_4c884a((uint8_t)value,(uint8_t)bits);
            shift+=bits;
            if((uint8_t)shift>=8u) {shift=0u;--input;}
            --output;
        }
    }
    data[7]=(uint32_t)(uintptr_t)decoded;
    d[11]=(uint32_t)(uintptr_t)decoded;
    return 1u;
}
