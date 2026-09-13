/* SPDX-License-Identifier: MIT */
/* Recovered lock controls. Invalid handles deliberately follow CK804 shifts:
 * low six count bits are used; counts 32..63 produce zero, even for ROTL.
 * See pinned XuanTie emulator evidence in gx8002-power-lock-shifts.json. */
#include <stdint.h>
struct lock_state { uint32_t active, allocated; };
extern volatile struct lock_state open_cfw_gx8002_power_state;
static inline uint32_t lock_bit(uint32_t count)
{
#ifdef __csky__
    uint32_t value = 1;
    __asm__("lsl %0, %1" : "+r"(value) : "r"(count));
    return value;
#else
    count &= 63;
    return count < 32 ? UINT32_C(1) << count : 0;
#endif
}
static inline uint32_t unlock_mask(uint32_t count)
{
#ifdef __csky__
    uint32_t value = UINT32_MAX - 1;
    __asm__("rotl %0, %1" : "+r"(value) : "r"(count));
    return value;
#else
    count &= 63;
    return count < 32 ? ~(UINT32_C(1) << count) : 0;
#endif
}

int open_cfw_gx8002_power_lock(int32_t lock)
{
    uint32_t bit = lock_bit((uint32_t)lock - 1);
    if (!(open_cfw_gx8002_power_state.allocated & bit)) return -1;
    if (lock > 32) return -1;
    open_cfw_gx8002_power_state.active |= bit;
    return 0;
}
int open_cfw_gx8002_power_unlock(int32_t lock)
{
    if (lock > 32) return -1;
    uint32_t keep = unlock_mask((uint32_t)lock - 1);
    open_cfw_gx8002_power_state.active &= keep;
    return 0;
}
