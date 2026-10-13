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
/* Native5138a4..513924: source-owned six startup words at513ea8. */
void audio_uart_nema_child_5138a4(void) {
    uint32_t words[6]={0u,0u,0x08000002u,0x80000009u,0u,0u};
    audio_uart_nema_instruction_upload_522920(words,1u,24u);
    audio_uart_nema_instruction_upload_522920(words,1u,25u);
    audio_uart_nema_instruction_upload_522920(words,1u,26u);
    audio_uart_nema_instruction_upload_522920(words,1u,27u);
    audio_uart_nema_instruction_upload_522920(words,1u,28u);
    audio_uart_nema_instruction_upload_522920(words,1u,29u);
    audio_uart_nema_instruction_upload_522920(words,1u,30u);
    audio_uart_nema_instruction_upload_522920(words+2,1u,31u);
    uint32_t capabilities=audio_uart_nema_child_522602();
    volatile uint8_t *state=(void *)(uintptr_t)0x200043a8u;
    uint32_t enabled=(capabilities>>28)&1u;
    state[0]=(uint8_t)enabled;
    if(enabled!=0u) {
        *(volatile uint32_t *)(state+4u)=0u;
        audio_uart_nema_rop_blend_mode_522956(1u);
    }
}
