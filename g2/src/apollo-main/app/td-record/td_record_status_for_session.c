/* Apollo status lookup for a session, native 0x5973e4. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

/* Stock 0x5973E4 (td_record_status_get) */
uint8_t audio_td_record_status_for_session(uint32_t session) {
    if(session==UINT32_MAX) return audio_td_state[0x95f2u];
    if(session==0u || audio_td_state[0xa1d9u]==0u) return 0u;
    uint32_t count=load_u32(audio_td_state+0x9568u);
    if(count>10u) count=10u;
    for(uint32_t i=0;i<count;++i) {
        uint32_t row=i*0x90u;
        if(load_u32(audio_td_state+0x95fcu+row)==session)
            return audio_td_state[0x9682u+row];
    }
    return 0u;
}
