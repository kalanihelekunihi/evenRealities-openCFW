/* Terminal-data active-session flag getter, native 0x5973aa..0x5973b1
 * (firmware 2.2.6.10). The pool word 0x597c10 holds 0x20119ef9, which is
 * byte 0xa1d9 of the terminal-data state block at RAM 0x2010fd20.
 * td_has_active_session (0x5973b2) and td_session_bind_store (0x5979b2)
 * read and set the same byte. */
#include <stdint.h>

extern uint8_t audio_td_state[0xa1dc]; /* RAM 0x2010fd20 */

uint8_t td_flag_get(void)
{
    return audio_td_state[0xa1d9u];
}
