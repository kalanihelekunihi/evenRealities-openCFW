/* Apollo current-session index helpers 0x5eca48/5ecaac/5ecafa. */
#include <stdint.h>

extern uint8_t *audio_td_active_session(void);
extern uint8_t audio_td_has_active_session(void);

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_td_active_record_count(void) {
    const uint8_t *active=audio_td_active_session();
    if(active==0) return 0;
    uint32_t count=load_u32(active+8u);
    return count>10u?10u:count;
}

int32_t audio_td_current_session_index_signed(void) {
    const uint8_t *active=audio_td_active_session();
    if(active==0) return -1;
    uint32_t count=audio_td_active_record_count();
    uint32_t current=load_u32(active+4u);
    for(uint32_t i=0;i<count;++i) {
        if(load_u32(active+0x9cu+i*0x90u)==current)
            return (int16_t)i;
    }
    return audio_td_has_active_session()!=0u?-1:-2;
}

uint16_t audio_td_current_session_index(void) {
    return (uint16_t)(int16_t)audio_td_current_session_index_signed();
}
