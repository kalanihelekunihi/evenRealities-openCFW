/* Apollo record status read wrapper, native 0x597446. */
#include <stdint.h>
extern uint32_t audio_td_counter_b_get(void);
extern uint8_t audio_td_record_status_for_session(uint32_t);

/* Stock 0x597446 (td_record_status_read) */
uint8_t audio_td_record_status_read(void) {
    return audio_td_record_status_for_session(audio_td_counter_b_get());
}
