#include <stdint.h>
extern void *audio_uart_nema_node_allocate_51416c(uint32_t);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,uint32_t);
extern void audio_uart_nema_matrix_identity_561810(void *);
/* Native515096..5150ea: sparse paint initialization; untouched fields preserved. */
void *audio_uart_nema_vg_paint_create_515096(void) {
 volatile uint8_t *paint=audio_uart_nema_node_allocate_51416c(220u);
 if(!paint){audio_uart_nema_vg_set_error_51565c(1u);return (void *)paint;}
 *(volatile uint32_t *)(paint+0)=0;*(volatile uint32_t *)(paint+4)=0;
 paint[44]=0;paint[213]=0;paint[204]=0;
 *(volatile uint32_t *)(paint+48)=0;
 *(volatile uint32_t *)(paint+208)=0x3f800000u;
 *(volatile uint32_t *)(paint+216)=0xff000000u;
 audio_uart_nema_matrix_identity_561810((void *)(paint+52));
 audio_uart_nema_matrix_identity_561810((void *)(paint+8));
 paint[212]=0;return (void *)paint;
}
/* Native51510e..515136: buffer creation precedes unchecked output store. */
void *audio_uart_nema_vg_grad_create_51510e(void) {
 uint32_t *gradient=audio_uart_nema_node_allocate_51416c(16u);uint32_t descriptor[4];
 audio_uart_nema_buffer_create_514070(descriptor,1u,256u);
 gradient[0]=descriptor[0];gradient[1]=descriptor[1];gradient[2]=descriptor[2];gradient[3]=descriptor[3];
 return gradient;
}
