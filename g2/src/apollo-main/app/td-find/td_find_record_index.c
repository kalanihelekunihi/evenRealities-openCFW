/* Apollo record index lookup, native 0x597138. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

/* Stock 0x597138 (td_find_record_index) */
uint32_t audio_td_find_record_index(uint32_t session,uint32_t *index) {
    if(session==0u || index==0 || audio_td_state[0xa1d9u]==0u) return 0u;
    uint32_t count=load_u32(audio_td_state+0x9568u);
    if(count>10u) count=10u;
    for(uint32_t i=0;i<count;++i) {
        if(load_u32(audio_td_state+0x95fcu+i*0x90u)==session) {
            *index=i;
            return 1u;
        }
    }
    return 0u;
}
