/* Apollo td_record_flags_clear_all, native 0x597664. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native RAM base 0x2010fd20 */

void audio_td_record_flags_clear_all(void) {
    const uint8_t *count_bytes=audio_td_state+0x9568u;
    uint32_t count=(uint32_t)count_bytes[0]
                  |((uint32_t)count_bytes[1]<<8)
                  |((uint32_t)count_bytes[2]<<16)
                  |((uint32_t)count_bytes[3]<<24);
    if(count>10u) count=10u;
    volatile uint8_t *state=audio_td_state;
    for(uint32_t i=0;i<count;++i) {
        uint32_t offset=0x9684u+i*0x90u;
        for(uint32_t j=0;j<4u;++j) state[offset+j]=0;
    }
    for(uint32_t j=0;j<4u;++j) state[0x95f4u+j]=0;
}
