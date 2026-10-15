/* Image-path name for the selected native 0x4b1298 texture binder. */
#include <stdint.h>

extern void audio_uart_nema_bind_tex_4b1298(uint32_t,uint32_t,uint32_t,
                                             uint32_t,uint32_t,uint32_t,
                                             uint32_t);

void audio_uart_ambiq_texture_bind_4b1298(uint32_t unit,uint32_t address,
                                            uint32_t width,uint32_t height,
                                            uint32_t format,uint32_t stride,
                                            uint32_t flags) {
    audio_uart_nema_bind_tex_4b1298(unit,address,width,height,format,
                                    stride,flags);
}
