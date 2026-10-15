/* Apollo Ambiq image option and texture setup at native 0x4b0d38. */
#include <stdint.h>
extern uint32_t audio_uart_ambiq_nema_cf_4b05a4(uint32_t);
extern void audio_uart_ambiq_texture_bind_4b1298(uint32_t,uint32_t,uint32_t,
                                                   uint32_t,uint32_t,uint32_t,
                                                   uint32_t);
extern void audio_uart_ambiq_texture_color_4b146c(uint32_t);
extern void audio_uart_ambiq_image_alpha_513e2e(uint32_t);
uint32_t audio_uart_ambiq_image_options_4b0d38(const uint32_t *image,
                                                uint32_t color,uint32_t mode) {
    const uint32_t format=(image[0]>>8)&0xffu;
    const uint32_t nema_format=audio_uart_ambiq_nema_cf_4b05a4(format);
    uint32_t flags=0u;
    uint32_t offset=0u;
    if(format>=7u && format<=10u) {
        flags|=0x200000u;
        offset=(format==7u)?2u:(format==8u)?4u:(format==9u)?16u:256u;
        audio_uart_ambiq_texture_bind_4b1298(2u,image[4],offset,1u,
                                               16u,0u,4u);
    }
    audio_uart_ambiq_texture_color_4b146c(
        format>=11u && format<=14u ? (color|0xff000000u) : 0u);
    if(format==20u) {
        uint32_t dimensions=image[1];
        uint32_t width=dimensions&0xffffu;
        uint32_t height=dimensions>>16;
        audio_uart_ambiq_texture_bind_4b1298(
            3u,image[4]+(image[2]&0xffffu)*height,width,height,
            8u,0xffffffffu,8u);
        flags|=0x800000u;
    }
    if((color>>24)<0xfdu) {
        flags|=0x8000000u;
        audio_uart_ambiq_image_alpha_513e2e(color&0xff000000u);
    }
    const uint32_t dimensions=image[1];
    audio_uart_ambiq_texture_bind_4b1298(
        1u,image[4]+offset*4u,dimensions&0xffffu,dimensions>>16,
        nema_format,image[2]&0xffffu,(mode|1u)&0xffu);
    return flags;
}
