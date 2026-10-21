/* Apollo terminal-data flag and temporary-record reset, 0x5971cc/1f6/572. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native RAM 0x2010fd20 */

static uint32_t load_u32(const volatile uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void put_u32(volatile uint8_t *p,uint32_t value) {
    for(uint32_t i=0;i<4u;++i) p[i]=(uint8_t)(value>>(8u*i));
}
static void clear_temp(void) {
    volatile uint8_t *state=audio_td_state;
    for(uint32_t i=0;i<0x90u;++i) state[0x956cu+i]=0;
}

void audio_td_temp_record_clear(void) {
    volatile uint8_t *state=audio_td_state;
    clear_temp();
    if(load_u32(state+0x9564u)==UINT32_MAX)
        put_u32(state+0x9564u,0u);
}

void audio_td_temp_record_invalidate(void) {
    volatile uint8_t *state=audio_td_state;
    clear_temp();
    put_u32(state+0x956cu,UINT32_MAX);
    state[0x956cu+0x86u]=0;
    put_u32(state+0x9564u,UINT32_MAX);
    state[0xa1dau]=1;
}

void audio_td_flag_set_with_reset(uint8_t enabled) {
    volatile uint8_t *state=audio_td_state;
    if(enabled!=0u) audio_td_temp_record_invalidate();
    else {
        state[0xa1dau]=0;
        audio_td_temp_record_clear();
    }
}
