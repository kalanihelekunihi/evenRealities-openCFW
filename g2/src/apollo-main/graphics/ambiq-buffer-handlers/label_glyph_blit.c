/* Apollo Ambiq raw glyph bitmap draw at native 0x53fb18..0x53fcc1. */
#include <stdint.h>
#include <stddef.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);
extern void display_driver_gpu_enable_4b0748(uint32_t,uint32_t);
extern void audio_uart_ambiq_image_alpha_513e2e(uint32_t);
extern void audio_uart_ambiq_texture_color_4b146c(uint32_t);
extern void audio_uart_nema_matrix_identity_561810(float *);
extern void display_driver_gpu_blit_4b1608(void *,uint32_t,uint32_t,
                                          uint32_t,uint32_t,uint32_t);
extern void audio_uart_nema_matrix_translate_561856(float,float,float *)
    __attribute__((pcs("aapcs-vfp")));
extern void audio_uart_nema_matrix_upload_5226e8(const float *);
extern void display_driver_nema_clear_522ae0(uint32_t,uint32_t,uint32_t,
                                             uint32_t);
static const char glyph_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_letter.c";
static const char glyph_function[]="draw_raw_bitmap_internal";
static const char glyph_bad_format[]="Unsupported format!";
static const char glyph_null[]="NULL pointer";
static const char glyph_null_expr[]="bitmap != NULL";
static const char glyph_assert[]="Asserted at expression: %s (%s)";
void audio_uart_ambiq_label_glyph_blit_53fb18(uint32_t unit,void *bitmap,
       uint32_t width,uint32_t height,const int32_t *clip,uint32_t depth,
       uint32_t color,uint32_t row_mode,uint32_t compact) {
    uint32_t nema_format;
    switch(depth&0xffu) {
    case 1u:case 17u:nema_format=12u;break;
    case 2u:case 18u:nema_format=48u;break;
    case 4u:case 20u:nema_format=52u;break;
    case 8u:case 24u:nema_format=8u;break;
    default:
        audio_uart_lvgl_log(3u,glyph_path,0x70u,glyph_function,
                            glyph_bad_format);
        return;
    }
    if((color&0xff000000u)==0xff000000u)
        display_driver_gpu_enable_4b0748(unit,0x504u);
    else {
        display_driver_gpu_enable_4b0748(unit,0x8000504u);
        audio_uart_ambiq_image_alpha_513e2e(color);
    }
    audio_uart_ambiq_texture_color_4b146c(color);
    float matrix[9];
    audio_uart_nema_matrix_identity_561810(matrix);
    if(bitmap==NULL) {
        audio_uart_lvgl_log(3u,glyph_path,0x82u,glyph_function,
                            glyph_assert,glyph_null_expr,glyph_null);
        for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
    }
    if(row_mode&0xffu) {
        if((compact&0xffu)!=0u && (width&1u)==0u) width+=2u;
        display_driver_gpu_blit_4b1608(bitmap,width,height,nema_format,
                                       UINT32_MAX,0u);
        audio_uart_nema_matrix_translate_561856(
            (float)(int32_t)(0u-(uint32_t)clip[0]),
            (float)(int32_t)(0u-(uint32_t)clip[1]),matrix);
    } else {
        display_driver_gpu_blit_4b1608(bitmap,width*height,1u,nema_format,
                                       0u,0u);
        matrix[1]=(float)(int32_t)width;
        const int32_t offset=(int32_t)(0u-(uint32_t)clip[0]-
                                       width*(uint32_t)clip[1]);
        matrix[2]=(float)offset-(float)(int32_t)width*0.5f;
    }
    audio_uart_nema_matrix_upload_5226e8(matrix);
    display_driver_nema_clear_522ae0((uint32_t)clip[0],(uint32_t)clip[1],
        (uint32_t)clip[2]-(uint32_t)clip[0]+1u,
        (uint32_t)clip[3]-(uint32_t)clip[1]+1u);
}
