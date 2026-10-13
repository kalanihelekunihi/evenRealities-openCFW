#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
/* Native5144ba..5144fa: cached context/list, wrapped signed capacity test. */
void audio_uart_nema_cl_unbind_5144ba(void) {
    volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    volatile uint32_t *list=(volatile uint32_t *)(uintptr_t)context[1];
    if(list) {
        uint32_t used=list[5];
        uint32_t capacity=list[4];
        if((int32_t)capacity >= (int32_t)(used+2u)) {
            volatile uint32_t *commands=(volatile uint32_t *)(uintptr_t)list[2];
            commands[used]=0x50000u;
            commands[used+1u]=0u;
            list[6]=list[6]&~8u;
        }
        list[6]=list[6]&~32u;
    }
    context[1]=0u;
}
