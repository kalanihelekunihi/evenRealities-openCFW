#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_framebuffer_descriptor_200732e8[];
extern void audio_uart_nema_cl_buffer_destroy_5140c6(void *);
/* Native5155dc..5155e4: fixed framebuffer descriptor uses real destroy contract. */
void audio_uart_nema_vg_framebuffer_destroy_5155dc(void) {
 audio_uart_nema_cl_buffer_destroy_5140c6((void *)audio_uart_nema_vg_framebuffer_descriptor_200732e8);
}
