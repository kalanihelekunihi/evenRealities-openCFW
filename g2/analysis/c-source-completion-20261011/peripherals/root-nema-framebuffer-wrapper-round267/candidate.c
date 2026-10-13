#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_framebuffer_context_cell_20074f08;
extern void audio_uart_nema_vg_framebuffer_destroy_5155dc(void);
extern void audio_uart_nema_vg_framebuffer_store_5155e4(uint32_t,uint32_t,audio_uart_vg_framebuffer_264);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
/* Native5223a2..5223fa: conditional cleanup, by-value store, fresh context reload. */
void audio_uart_nema_vg_set_framebuffer_5223a2(uint32_t width,uint32_t height,audio_uart_vg_framebuffer_264 framebuffer) {
 const volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_vg_framebuffer_context_cell_20074f08;
 if(context[24u]&1u)audio_uart_nema_vg_framebuffer_destroy_5155dc();
 audio_uart_nema_vg_framebuffer_store_5155e4(width,height,framebuffer);
 context=(void *)(uintptr_t)audio_uart_nema_vg_framebuffer_context_cell_20074f08;
 if((context[16u]&3u)!=0u || (context[20u]&3u)!=0u)audio_uart_nema_vg_set_error_51565c(0x2000000u);
}
