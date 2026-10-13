#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_framebuffer_descriptor_200732e8[];
/* Native5155e4..51562e: ordered descriptor writes and signed-to-float dimensions. */
void audio_uart_nema_vg_framebuffer_store_5155e4(uint32_t width,uint32_t height,audio_uart_vg_framebuffer_264 framebuffer) {
 volatile uint32_t *d=audio_uart_nema_vg_framebuffer_descriptor_200732e8;
 volatile float *f=(volatile float *)(void *)d;
 d[4]=width;
 float w=(float)(int32_t)width;f[9]=w;f[11]=w;
 float h=(float)(int32_t)height;
 d[0]=framebuffer.words[0];d[1]=framebuffer.words[1];d[2]=framebuffer.words[2];d[3]=framebuffer.words[3];
 d[5]=height;d[7]=0;d[8]=0;d[10]=0;f[12]=h;d[13]=0;f[14]=h;
}
/* Native51562e..515634: address only; no storage initializer inferred. */
void *audio_uart_nema_vg_framebuffer_get_51562e(void) {return (void *)audio_uart_nema_vg_framebuffer_descriptor_200732e8;}
