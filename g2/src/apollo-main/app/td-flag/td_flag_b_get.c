/* Apollo flag-B getter, native 0x59758e. */
#include <stdint.h>
extern uint8_t audio_td_state[0xa1dc];
/* Stock 0x59758E (td_flag_b_get) */
uint8_t audio_td_flag_b_get(void) {return audio_td_state[0xa1dau];}
