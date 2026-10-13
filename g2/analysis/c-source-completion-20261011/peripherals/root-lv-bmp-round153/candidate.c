#include <stdint.h>
extern const char *audio_uart_lv_fs_extension_4c70e4(const char *);
extern int32_t audio_uart_lv_string_compare_4547be(const char *,const char *);
extern uint32_t audio_uart_lv_fs_file_read_4c6f46(void *,void *,uint32_t,uint32_t *);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char bmp_format[]="Not supported bpp: %d";
static const char bmp_function[]="decoder_info";
static const char bmp_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\bmp\\lv_bmp.c";
/* Native4c91e0..4c92a8; file type1, packed16-bit dimensions and byte8cf. */
uint32_t audio_uart_lv_bmp_info_4c91e0(void *decoder,void *descriptor,void *header) {
    (void)decoder;
    volatile uint8_t *d=descriptor;
    const char *src=(const char *)(uintptr_t)*(volatile uint32_t *)(d+12u);
    uint8_t type=d[16];
    if(type!=1u)return 0u;
    if(audio_uart_lv_string_compare_4547be(audio_uart_lv_fs_extension_4c70e4(src),"bmp")!=0)return 0u;
    uint8_t bytes[54];uint32_t width,height;uint16_t bpp;
    (void)audio_uart_lv_fs_file_read_4c6f46((void *)(d+20u),bytes,54u,0);
    audio_uart_lv_grid_copy_454738(&width,bytes+18u,4u);
    audio_uart_lv_grid_copy_454738(&height,bytes+22u,4u);
    volatile uint32_t *h=header;
    h[1]=(h[1]&0xffff0000u)|(width&0xffffu);
    h[1]=(h[1]&0x0000ffffu)|(height<<16);
    audio_uart_lv_grid_copy_454738(&bpp,bytes+28u,2u);
    uint32_t cf;
    switch(bpp) {
    case 16:cf=18u;break;
    case 24:cf=15u;break;
    case 32:cf=16u;break;
    default:audio_uart_lvgl_log(2u,bmp_path,126u,bmp_function,bmp_format,(uint32_t)bpp);return 1u;
    }
    h[0]=(h[0]&0xffff00ffu)|(cf<<8);
    return 1u;
}
