/* Apollo current-record pointer lookup, native 0x597188. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];
extern uint32_t audio_td_find_record_index(uint32_t,uint32_t *);

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

/* Stock 0x597188 (td_current_record) */
uint8_t *audio_td_current_record(uint32_t session) {
    if(session==UINT32_MAX)
        return load_u32(audio_td_state+0x956cu)==UINT32_MAX?
               audio_td_state+0x956cu:(uint8_t *)0;
    uint32_t index=0u;
    if(audio_td_find_record_index(session,&index)==0u) return (uint8_t *)0;
    return audio_td_state+0x95fcu+index*0x90u;
}
