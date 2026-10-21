/* Apollo td_session_bind_store 0x5979b2 and td_has_active_session 0x5973b2. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native RAM 0x2010fd20 */

static uint32_t load_u32(const volatile uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_u32(volatile uint8_t *p,uint32_t value) {
    for(uint32_t i=0;i<4u;++i) p[i]=(uint8_t)(value>>(8u*i));
}

void audio_td_session_bind_store(uint32_t session) {
    volatile uint8_t *state=audio_td_state;
    put_u32(state+0x9564u,session);
    if(load_u32(state+0x9560u)!=0u) state[0xa1d9u]=1u;
}

uint8_t audio_td_has_active_session(void) {
    const volatile uint8_t *state=audio_td_state;
    return (uint8_t)(state[0xa1d9u]!=0u && load_u32(state+0x9560u)!=0u);
}
