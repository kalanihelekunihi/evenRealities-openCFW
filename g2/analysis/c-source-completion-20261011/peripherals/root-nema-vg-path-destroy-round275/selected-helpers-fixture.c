#include <stdint.h>
extern volatile uint32_t audio_uart_nema_vg_context_cell;
extern void audio_uart_lv_pool_free_48429e(void *,void *);
void audio_uart_nema_matrix_identity_561810(void *cell) {
 volatile uint32_t *matrix=cell;
 matrix[0]=0x3f800000u;matrix[1]=0;matrix[2]=0;matrix[3]=0;
 matrix[4]=0x3f800000u;matrix[5]=0;matrix[6]=0;matrix[7]=0;matrix[8]=0x3f800000u;
}
void audio_uart_nema_vg_set_error_51565c(uint32_t error) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_vg_context_cell;
    context[32]=context[32]|error;
}
void audio_uart_nema_cl_node_release_514178(void *node) {
    audio_uart_lv_pool_free_48429e((void *)(uintptr_t)0x20000338u,node);
}