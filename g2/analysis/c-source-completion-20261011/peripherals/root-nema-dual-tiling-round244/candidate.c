#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
/* Native52264e..52266e: dual tiling state, distinct mask from52262e. */
void audio_uart_nema_child_52264e(uint32_t enabled){
 uint32_t flags=enabled?0xc0000000u:0u;
 volatile uint32_t *context=(volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
 context[3]=flags;uint32_t a=context[5];uint32_t b=context[4];uint32_t c=context[7];
 context[6]=flags|a|b|c;
}
