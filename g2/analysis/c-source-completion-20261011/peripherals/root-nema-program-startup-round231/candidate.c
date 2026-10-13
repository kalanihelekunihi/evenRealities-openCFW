#include <stdint.h>
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
extern uint32_t audio_uart_nema_child_522602(void);
/* Native522920..52294c: address command precedes zero-count gate, two words per upload. */
void audio_uart_nema_instruction_upload_522920(const uint32_t *words,uint32_t count,uint32_t address) {
    audio_uart_nema_child_514846(196u,address);
    while(count!=0u) {
        const volatile uint32_t *p=words;
        audio_uart_nema_child_514846(200u,p[0]);
        uint32_t second=p[1];words=(void *)((uintptr_t)words+8u);
        audio_uart_nema_child_514846(204u,second);count--;
    }
}
/* Native522956..522960: command464 scalar wrapper. */
void audio_uart_nema_rop_blend_mode_522956(uint32_t value) {audio_uart_nema_child_514846(464u,value);}
