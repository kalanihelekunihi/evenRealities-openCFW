/* Apollo terminal-data pointer getters 0x597318/31e/324. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* native RAM 0x2010fd20 */

const uint8_t *audio_td_state_ptr(void) {return audio_td_state;}
uint8_t *audio_td_session_struct_ptr(void) {return audio_td_state+0x808u;}
uint8_t *audio_td_ring_ptr(void) {return audio_td_state+0x1054u;}
