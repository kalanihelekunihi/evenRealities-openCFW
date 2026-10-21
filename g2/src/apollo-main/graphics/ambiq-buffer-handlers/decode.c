/* Apollo Ambiq image decoder wrapper at 0x4b0f50..0x4b1035. */
#include <stdint.h>

extern uint32_t audio_uart_lv_image_decoder_open_488f9c(
    void *,const void *,const void *,uint32_t);
extern void audio_uart_lv_image_decoder_close_48908c(void *);
extern int32_t audio_uart_ambiq_color_format_src_4b05a4(uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char decode_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
static const char decode_name[] = "lv_draw_ambiq_decode_image";
static const char decode_open_error[] = "Failed to open image";
static const char decode_ram_error[] =
    "Ambiq GPU needs to load the whole image to GPU accessible RAM.\n";
static const char decode_format_error[] =
    "GPU failed, not supported color format!";
static const char decode_mask_error[] =
    "The mask image is not A8/L8 format. We will ignore it.";

uint32_t audio_uart_ambiq_decode_image_4b0f50(
        const void *image,uint32_t transformed,void *decode_result,
        uint32_t mask) {
    uint8_t options[8] = {0u,0u,0u,(uint8_t)!((uint8_t)transformed),1u,0u,0u,0u};
    const uint32_t opened=audio_uart_lv_image_decoder_open_488f9c(
        decode_result,image,options,mask);
    if ((opened&0xffu)!=1u) {
        audio_uart_lvgl_log(3u,decode_path,0x2c4u,decode_name,
                            decode_open_error);
        return opened&0xffu;
    }
    const uint32_t header=*(const uint32_t *)(const void *)
        ((const uint8_t *)decode_result+0x2cu);
    if (header==0u) {
        audio_uart_lv_image_decoder_close_48908c(decode_result);
        audio_uart_lvgl_log(2u,decode_path,0x2cbu,decode_name,
                            decode_ram_error);
        return 0u;
    }
    const uint32_t color_format=
        (*(const uint32_t *)(uintptr_t)header>>8)&0xffu;
    if (audio_uart_ambiq_color_format_src_4b05a4(color_format)==-1) {
        audio_uart_lv_image_decoder_close_48908c(decode_result);
        audio_uart_lvgl_log(2u,decode_path,0x2d5u,decode_name,
                            decode_format_error);
        return 0u;
    }
    if (((uint8_t)mask)!=0u && color_format!=14u && color_format!=6u) {
        audio_uart_lvgl_log(2u,decode_path,0x2dbu,decode_name,
                            decode_mask_error);
        audio_uart_lv_image_decoder_close_48908c(decode_result);
        return 0u;
    }
    return 1u;
}
