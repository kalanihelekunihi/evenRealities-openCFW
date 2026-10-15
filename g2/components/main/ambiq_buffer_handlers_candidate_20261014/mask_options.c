/* Apollo Ambiq mask texture options at 0x4b0ea6..0x4b0f4e. */
#include <stdint.h>

extern uint32_t audio_uart_ambiq_nema_cf_4b05a4(uint32_t);
extern void audio_uart_ambiq_texture_bind_4b1298(uint32_t,uint32_t,
        uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_ambiq_texture_setup_4b06c0(uint32_t,uint32_t,
        uint32_t,uint32_t,uint32_t,uint32_t);
extern void audio_uart_ambiq_mask_position_4b1ad4(uint32_t,uint32_t,
        uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char mask_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_private.c";
static const char mask_function[]="lv_draw_ambiq_bind_mask_texture";
static const char mask_message[]="Asserted at expression: %s";
static const char mask_expression[]="(nema_cf == NEMA_A8) || (nema_cf == NEMA_L8)";

uint32_t audio_uart_ambiq_mask_options_4b0ea6(const void *texture,
                                                uint32_t enable) {
    const uint32_t *const t=(const uint32_t *)texture;
    const uint32_t format=audio_uart_ambiq_nema_cf_4b05a4((t[0]>>8)&0xffu);
    if (format!=8u && format!=9u) {
        audio_uart_lvgl_log(3u,mask_path,663u,mask_function,
                            mask_message,mask_expression);
        *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
        for (;;) {}
    }
    const uint32_t width=t[1]&0xffffu;
    const uint32_t height=t[1]>>16;
    const uint32_t stride=t[2]&0xffffu;
    if ((enable&0xffu)!=0u) {
        audio_uart_ambiq_texture_bind_4b1298(2u,t[4],width,height,
                                               8u,stride,8u);
        audio_uart_ambiq_texture_setup_4b06c0(0u,6u,3u,2u,
                                                0xffffffffu,0u);
        audio_uart_ambiq_mask_position_4b1ad4(0u,0u,width,height);
    } else {
        audio_uart_ambiq_texture_bind_4b1298(3u,t[4],width,height,
                                               8u,stride,8u);
    }
    return 0x00800000u;
}
