/* Stock td_counter_b_get 0x5973dc delegates to existing C-owned RAM getter. */
#include <stdint.h>
extern uint32_t audio_td_counter_b_get(void);
uint32_t audio_terminal_counter_b_get_5973dc(void) {
    return audio_td_counter_b_get();
}
