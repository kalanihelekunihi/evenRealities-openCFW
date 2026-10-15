/* QuickList cache timestamp calls native 0x44a1c6, the same routine already
 * reconstructed as audio_log_context in the selected Main source graph. */
#include <stdint.h>

extern uint32_t audio_log_context(void);

uint32_t audio_quicklist_tick_now(void) {
    return audio_log_context();
}
