#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[]; /* RAM20074efc */
extern void audio_uart_nema_error_set_4b127c(uint32_t);
extern void audio_uart_nema_cl_buffer_destroy_5140c6(void *);
extern void audio_uart_nema_cl_node_release_514178(void *);
/* Native5142f0..514382; command words are data for the GPU command buffer. */
void audio_uart_nema_cl_destroy_5142f0(void *command_list) {
    volatile uint32_t *cl=command_list;
    if(cl==0) {audio_uart_nema_error_set_4b127c(8192u);return;}
    uint32_t root=cl[9];
    if(root!=0u&&(((volatile uint8_t *)cl)[24]&32u)==0u)
        cl=(volatile uint32_t *)(uintptr_t)root;
    do {
        volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
        if(context[1]==(uint32_t)(uintptr_t)cl) {
            uint32_t offset=cl[5];uint32_t size=cl[4];
            if((int32_t)size>=(int32_t)(offset+2u)) {
                volatile uint32_t *commands=(void *)(uintptr_t)cl[2];
                commands[offset]=0x50000u;
                commands[offset+1u]=0u;
                cl[6]=cl[6]&~8u;
            }
            cl[6]=cl[6]&~32u;
            context[1]=0u;
        }
        if((((volatile uint8_t *)cl)[24]&16u)!=0u)cl=(void *)(uintptr_t)cl[8];
        else {
            audio_uart_nema_cl_buffer_destroy_5140c6((void *)cl);
            uint32_t root_after=cl[9];uint32_t next=cl[8];
            if(root_after!=0u)audio_uart_nema_cl_node_release_514178((void *)cl);
            cl=(void *)(uintptr_t)next;
        }
    } while(cl!=0);
}
