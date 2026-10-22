/* Apollo td_session_struct_clear, native 0x597124. */
#include <stdint.h>

/* Native RAM 0x20110528 = cluster base + 0x808, length 0x84c. */
extern uint8_t audio_td_state[0xa1dc];

/* Stock 0x597124 (td_session_struct_clear) */
void audio_td_session_struct_clear(void) {
    volatile uint8_t *state=audio_td_state+0x808u;
    for(uint32_t i=0;i<0x84cu;++i) state[i]=0;
}
