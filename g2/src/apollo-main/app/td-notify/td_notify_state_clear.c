/* Apollo td_notify_state_clear, native 0x597110. */
#include <stdint.h>

/* Native RAM 0x2010fd20, length 0x806. Final linker placement remains open. */
extern uint8_t audio_td_state[0xa1dc];

void audio_td_notify_state_clear(void) {
    volatile uint8_t *state=audio_td_state;
    for(uint32_t i=0;i<0x806u;++i) state[i]=0;
}
