/* Native473482..4734a0; preserve callback reload and tick flag retry. */
#include <stdint.h>
extern uint8_t audio_uart_lv_tick_state[];
uint32_t audio_uart_lv_tick(void) {
    volatile uint8_t *state=audio_uart_lv_tick_state;
    if(*(volatile uint32_t *)(state+8u)!=0u) {
        uint32_t callback=*(volatile uint32_t *)(state+8u);
        return ((uint32_t (*)(void))(uintptr_t)callback)();
    }
    uint32_t tick;
    do {
        state[4u]=1u;
        tick=*(volatile uint32_t *)state;
    } while(state[4u]==0u);
    return tick;
}
