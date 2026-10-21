/* Apollo td_session_ring_reset 0x5970c0 and wrapper 0x597108. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native base 0x2010fd20 */
/* Native RAM 0x20074a88; final linker placement remains open. */
uint32_t audio_td_ring_reset_counter;

static void put_u32(volatile uint8_t *dst,uint32_t value) {
    for(uint32_t i=0;i<4u;++i) dst[i]=(uint8_t)(value>>(8u*i));
}

void audio_td_session_ring_reset(void) {
    uint32_t sequence=audio_td_ring_reset_counter+1u;
    audio_td_ring_reset_counter=sequence;
    volatile uint8_t *ring=audio_td_state+0x1054u; /* native 0x20110d74 */
    for(uint32_t i=0;i<0x850cu;++i) ring[i]=0;
    put_u32(ring+0x8504u,sequence);
    put_u32(ring+0x8508u,1u);
}

void audio_td_ring_reset_wrapper(void) {
    audio_td_session_ring_reset();
}
