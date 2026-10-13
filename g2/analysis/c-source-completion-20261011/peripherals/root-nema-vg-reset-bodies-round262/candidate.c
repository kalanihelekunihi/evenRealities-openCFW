#include <stdint.h>
extern void audio_uart_nema_matrix_identity_561810(void *);
extern void audio_uart_nema_vg_set_error_51565c(uint32_t);
extern volatile uint32_t audio_uart_nema_vg_context_cell;
/* Native514e50..514eba: NULL error precedes all path stores. */
void audio_uart_nema_vg_path_reset_514e50(void *cell) {
 if(!cell){audio_uart_nema_vg_set_error_51565c(1u);return;}
 audio_uart_nema_matrix_identity_561810((void *)(uintptr_t)((uint32_t)(uintptr_t)cell+96u));
 volatile uint32_t *path=cell;
 path[33]=0;path[2]=0;path[3]=0;path[0]=0;path[1]=0;
 path[4]=0x477fff00u;path[5]=0x477fff00u;path[6]=0xc77fff00u;path[7]=0xc77fff00u;
 path[20]=0;path[21]=0;path[9]=0;path[8]=0;path[11]=0;path[10]=0;
 path[13]=0;path[12]=0;path[15]=0;path[14]=0;path[22]=0;path[23]=0;
 path[16]=0x477fff00u;path[17]=0x477fff00u;path[18]=0xc77fff00u;path[19]=0xc77fff00u;
}
/* Native515048..515096: sparse paint reset, two ordered identity calls. */
void audio_uart_nema_vg_paint_reset_515048(void *cell) {
 volatile uint8_t *paint=cell;
 if(!paint){audio_uart_nema_vg_set_error_51565c(1u);return;}
 *(volatile uint32_t *)(paint+0u)=0;*(volatile uint32_t *)(paint+4u)=0;
 paint[44]=0;paint[213]=0;paint[204]=0;
 *(volatile uint32_t *)(paint+48u)=0;
 *(volatile uint32_t *)(paint+208u)=0x3f800000u;
 *(volatile uint32_t *)(paint+216u)=0xff000000u;
 audio_uart_nema_matrix_identity_561810((void *)(paint+52u));
 audio_uart_nema_matrix_identity_561810((void *)(paint+8u));
 paint[212]=0;
}
/* Native515676..5156aa: fresh context loads bracket real matrix calls. */
void audio_uart_nema_vg_state_reset_515676(void) {
 volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 context[445u]=context[144u]&1u;
 context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 *(volatile uint32_t *)(context+144u)=*(volatile uint32_t *)(context+144u)&~1u;
 audio_uart_nema_matrix_identity_561810((void *)(context+164u));
 context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 audio_uart_nema_matrix_identity_561810((void *)(context+200u));
}
