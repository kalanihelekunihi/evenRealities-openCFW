/* Apollo td_active_session 0x59732a and cached status 0x5e830c. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native RAM 0x2010fd20 */

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint8_t *audio_td_active_session(void) {
    return audio_td_state[0xa1d9u]!=0u?audio_td_state+0x9560u:0;
}

uint8_t audio_terminal_cached_session_status(uint32_t session) {
    const uint8_t *active=audio_td_active_session();
    if(active==0) return 0;
    uint32_t count=load_u32(active+8u);
    for(uint32_t i=0;i<count;++i) {
        if(load_u32(active+0x9cu+i*0x90u)==session)
            return active[0x122u+i*0x90u];
    }
    return 0;
}
