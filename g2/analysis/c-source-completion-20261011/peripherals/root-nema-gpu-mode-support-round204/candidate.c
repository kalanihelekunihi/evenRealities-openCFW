#include <stdint.h>
extern volatile uint32_t audio_uart_nema_capabilities; /* authenticated RAM20074f00 */
extern volatile uint32_t audio_uart_nema_context_cell[];
extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t);
extern void audio_uart_nema_child_514846(uint32_t,uint32_t);
/* Native522602..52261a: zero cache triggers read, then fresh reread. */
uint32_t audio_uart_nema_child_522602(void) {
    if(audio_uart_nema_capabilities==0u)
        audio_uart_nema_capabilities=audio_uart_nema_reg_read_51403c(496u);
    return audio_uart_nema_capabilities;
}
/* Native52261a..522622. */
uint32_t audio_uart_nema_child_52261a(void) { return audio_uart_nema_reg_read_51403c(500u); }
/* Native52296a..522974. */
void audio_uart_nema_child_52296a(uint32_t mode) { audio_uart_nema_child_514846(480u,mode); }
/* Native52262e..52264e: saved context; ordered independent word reads. */
void audio_uart_nema_child_52262e(uint32_t enabled) {
    uint32_t flags=enabled?0x40000000u:0u;
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    context[3]=flags;
    uint32_t a=context[5];
    uint32_t b=context[4];
    uint32_t c=context[7];
    context[6]=flags|a|b|c;
}
