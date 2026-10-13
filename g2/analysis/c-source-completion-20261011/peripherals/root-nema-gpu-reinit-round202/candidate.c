#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern void audio_uart_nema_reg_write_514046(uint32_t,uint32_t);
extern void audio_uart_nema_cl_unbind_5144ba(void);
extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern void audio_uart_nema_child_523c88(void);
extern void audio_uart_nema_child_523304(uint32_t);
extern void audio_uart_nema_child_5138a4(void);
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
extern uint32_t audio_uart_nema_child_522602(void);
extern void audio_uart_nema_child_52296a(uint32_t);
extern void audio_uart_nema_child_52262e(uint32_t);
extern uint32_t audio_uart_nema_child_52261a(void);
/* Native4b11b0..4b127c. Keep fresh context-cell loads across child calls. */
int32_t audio_uart_nema_gpu_reinit_4b11b0(void) {
    if(audio_uart_nema_reg_read_51403c(492u)!=0x86362000u) {
        volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        context[8]=context[8]|2u;
        return -1;
    }
    audio_uart_nema_cl_unbind_5144ba();
    audio_uart_lv_memzero_48949c((void *)(uintptr_t)audio_uart_nema_context_cell[0],256u);
    audio_uart_nema_child_523c88();
    audio_uart_nema_reg_write_514046(232u,0u);
    audio_uart_nema_reg_write_514046(252u,0u);
    audio_uart_nema_reg_write_514046(904u,1u);
    audio_uart_nema_child_523304(0u);
    audio_uart_nema_child_5138a4();
    audio_uart_nema_child_514846(512u,0u);
    audio_uart_nema_child_514846(516u,UINT32_MAX);
    if(!(audio_uart_nema_child_522602()&(1u<<18))) {
        volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        context[10]=0u;
    } else {
        audio_uart_nema_child_52296a(7u);
        volatile uint8_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        context[9]=0u;
        context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        uint32_t a=context[8];
        uint32_t b=context[9];
        audio_uart_nema_child_52262e(a|b);
    }
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    context[5]=0u;
    uint32_t a=context[3],b=context[4],c=context[7];
    context[6]=a|b|c;
    if(audio_uart_nema_child_52261a()&(1u<<9)) {
        audio_uart_nema_reg_write_514046(884u,0u);
        audio_uart_nema_reg_write_514046(872u,0u);
    }
    return 0;
}
