/* Current-session status setter, stock 0x597452 via 0x597464. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* stock 0x2010fd20 */
extern uint32_t audio_terminal_counter_b_get_5973dc(void);

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

void audio_td_record_status_set_current_597452(uint32_t raw_status) {
    uint32_t session=audio_terminal_counter_b_get_5973dc();
    uint8_t status=(uint8_t)raw_status;
    if (session==UINT32_MAX) {
        audio_td_state[0x95f2u]=status;
        return;
    }
    if (session==0u || audio_td_state[0xa1d9u]==0u)return;
    uint32_t count=word(audio_td_state+0x9568u);
    if (count>10u)count=10u;
    for (uint32_t i=0u;i<count;i++) {
        uint32_t row=i*0x90u;
        if (word(audio_td_state+0x95fcu+row)!=session)continue;
        audio_td_state[0x9682u+row]=status;
        if (status!=2u)audio_td_state[0x9688u+row]=0u;
        return;
    }
}
