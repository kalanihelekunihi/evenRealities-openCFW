/* Native 0x48032c/0x480342 dispatch live platform callback slots +12/+16.
 * The table is populated at runtime by platform initialization. */
#include <stdint.h>
typedef uint32_t (*g2_power_callback)(void);
static uint32_t dispatch(unsigned slot) {
    g2_power_callback f = *(g2_power_callback volatile *)(uintptr_t)
        (0x20073270u + 4u*slot);
    return f ? f() : 0u;
}
uint32_t g2_power_tempco_postpone(void) { return dispatch(3u); }
uint32_t g2_power_tempco_pending(void) { return dispatch(4u); }
