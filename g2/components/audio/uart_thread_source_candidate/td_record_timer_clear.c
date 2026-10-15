/* Apollo record timer clear, native 0x597652. */
#include <stdint.h>
extern uint8_t *audio_td_current_record(uint32_t);

void audio_td_record_timer_clear(uint32_t session) {
    uint8_t *record=audio_td_current_record(session);
    if(record==0) return;
    for(uint32_t i=0;i<4u;++i) record[0x88u+i]=0u;
}
