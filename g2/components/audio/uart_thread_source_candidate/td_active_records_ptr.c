/* Apollo active record-array pointer, native 0x59732a. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];

uint8_t *audio_td_active_records_ptr(void) {
    return audio_td_state[0xa1d9u]!=0u ? audio_td_state+0x9560u : (uint8_t *)0;
}
