/* SPDX-License-Identifier: MIT */
/* Recovered LvpPmuSuspendLockCreate and LvpPmuSuspendIsLocked.
 * lvp_pmu.c lineage: 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Reload after publishing the handle preserves aliased output behavior. */
#include <stdint.h>
struct lock_state { uint32_t active, allocated; };
extern volatile struct lock_state open_cfw_gx8002_power_state;
#define STATE open_cfw_gx8002_power_state
int open_cfw_gx8002_power_lock_create(volatile int *lock)
{
    uint32_t allocated = STATE.allocated;
    for (unsigned i = 0; i < 32; ++i) {
        uint32_t bit = UINT32_C(1) << i;
        if (!(allocated & bit)) {
            *lock = (int)i + 1;
            STATE.allocated |= bit;
            return *lock;
        }
    }
    return -1;
}
int open_cfw_gx8002_power_is_locked(void)
{
    return STATE.active != 0;
}
