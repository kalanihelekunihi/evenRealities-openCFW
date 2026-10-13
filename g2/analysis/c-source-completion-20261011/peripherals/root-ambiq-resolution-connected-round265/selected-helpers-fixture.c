#include <stdint.h>
extern volatile uint32_t audio_uart_ambiq_unit_cell[];
extern volatile uint32_t audio_uart_nema_vg_context_cell;
void *audio_uart_ambiq_default_unit_4c791a(void) ;
void audio_uart_nema_vg_path_reset_514e50(void *cell) ;
void audio_uart_nema_vg_paint_reset_515048(void *cell) ;
void audio_uart_nema_vg_state_reset_515676(void) ;
void audio_uart_nema_matrix_identity_561810(void *cell) ;
void audio_uart_nema_vg_set_error_51565c(uint32_t error) ;
void audio_uart_ambiq_blend_clear_4b075e(void *unit) ;
void audio_uart_lv_memzero_48949c(void *destination,uint32_t size) ;
void *audio_uart_lv_word_fill_4d555c(void *destination,uint32_t size,uint32_t pattern) ;
void *audio_uart_ambiq_default_unit_4c791a(void) {
    return (void *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
}
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
void audio_uart_nema_vg_state_reset_515676(void) {
 volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 context[445u]=context[144u]&1u;
 context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 *(volatile uint32_t *)(context+144u)=*(volatile uint32_t *)(context+144u)&~1u;
 audio_uart_nema_matrix_identity_561810((void *)(context+164u));
 context=(void *)(uintptr_t)audio_uart_nema_vg_context_cell;
 audio_uart_nema_matrix_identity_561810((void *)(context+200u));
}
void audio_uart_nema_matrix_identity_561810(void *cell) {
 volatile uint32_t *matrix=cell;
 matrix[0]=0x3f800000u;matrix[1]=0;matrix[2]=0;matrix[3]=0;
 matrix[4]=0x3f800000u;matrix[5]=0;matrix[6]=0;matrix[7]=0;matrix[8]=0x3f800000u;
}
void audio_uart_nema_vg_set_error_51565c(uint32_t error) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    context[32]=context[32]|error;
}
void audio_uart_ambiq_blend_clear_4b075e(void *unit) {
    if(!unit)unit=audio_uart_ambiq_default_unit_4c791a();
    volatile uint8_t *u=unit;
    *(volatile uint32_t *)(u+80u)=0u;
    u[84]=255u;u[85]=255u;u[86]=255u;
}
void audio_uart_lv_memzero_48949c(void *destination,uint32_t size) {
    (void)audio_uart_lv_word_fill_4d555c(destination,size,0u);
}
void *audio_uart_lv_word_fill_4d555c(void *destination,uint32_t size,uint32_t pattern) {
    volatile uint8_t *p=destination;
    while(size>=16u) {
        *(volatile uint32_t *)(p+0u)=pattern;
        *(volatile uint32_t *)(p+4u)=pattern;
        *(volatile uint32_t *)(p+8u)=pattern;
        *(volatile uint32_t *)(p+12u)=pattern;
        p+=16u;size-=16u;
    }
    if(size&8u) {
        *(volatile uint32_t *)(p+0u)=pattern;
        *(volatile uint32_t *)(p+4u)=pattern;
        p+=8u;
    }
    if(size&4u){*(volatile uint32_t *)p=pattern;p+=4u;}
    if(size&2u){*(volatile uint16_t *)p=(uint16_t)pattern;p+=2u;}
    if(size&1u){*p=(uint8_t)pattern;p+=1u;}
    return (void *)p;
}