/* Apollo td_state_reset, native 0x5970f0. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native RAM 0x2010fd20 */
extern void audio_td_session_ring_reset(void);

void audio_td_state_reset(void) {
    volatile uint8_t *state=audio_td_state;
    for(uint32_t i=0;i<0xa1dcu;++i) state[i]=0;
    audio_td_session_ring_reset();
}
