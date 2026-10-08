/* Independently reconstructed leaf bodies from locked 42ad40 and 42b014. */
#include <stdint.h>

#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define U8(a)  (*(volatile uint8_t *)(uintptr_t)(a))

uint8_t native_spot_temperature_range(float value)
{
    if (value < -20.0f && value >= -273.0f) return 0;
    if (value >= -20.0f && value < 0.0f) return 1;
    if (value >= 0.0f && value < 50.0f) return 2;
    if (value >= 50.0f && value < 1000.0f) return 3;
    return 4;
}

void native_spot_transition_effect(uint8_t requested, uint8_t current)
{
    if (current == 1U && requested == 2U && U8(0x200271b2U) == 0U)
        U8(0x200271b0U) = 1U;
    if (current == 1U && requested == 0U) {
        U32(0x4002037cU) &= ~0x10000U;
        U32(0x4002037cU) &= ~0x08U;
        U32(0x4002037cU) &= ~0x40U;
        U8(0x200271b2U) = 0U;
    }
}

int native_spot_state_decode(const uint8_t *input, uint32_t *major,
                             uint32_t *minor)
{
    const uint32_t *word = (const uint32_t *)(const void *)input;
    uint32_t cfg = U32(0x434164U);
    uint32_t hw = U32(0x40021000U);
    uint32_t mode = U8(0x2002708cU);
    uint8_t state = input[17];
    uint8_t auxiliary = input[18];
    uint32_t flags = (cfg & 0xfffff0f0U) | ((input[16] & 0xfU) << 8);
    if (state == 1U) flags |= 1U;
    else if (state == 0U) flags &= ~1U;
    else if ((hw & 3U) == 2U) flags |= 1U;
    else flags &= ~1U;

    if (auxiliary == 1U || auxiliary == 2U ||
        (word[0] & 0x3fffffffU) != 0U || (word[1] & 0x4c4U) != 0U)
        flags = (flags & 0xffffff0fU) | 0x10U;
    else flags &= 0xffffff0fU;
    if (auxiliary == 2U) flags = (flags & 0xffff0fffU) | 0x2000U;
    else if (auxiliary == 1U) flags = (flags & 0xffff0fffU) | 0x1000U;
    else flags &= 0xffff0fffU;
    if ((word[0] & 0x3fffffffU) != 0U || (word[1] & 0x4c4U) != 0U)
        flags = (flags & 0xfff0ffffU) | 0x10000U;
    else flags &= 0xfff0ffffU;
    if ((word[0] & 0xc00000U) != 0U)
        flags = (flags & 0xff0fffffU) | 0x100000U;
    else flags &= 0xff0fffffU;

    uint32_t code = flags & 0xf00fffU;
    uint32_t m;
    switch (code) {
    case 0x000: m = mode & 1U ? 7U : 3U; break;
    case 0x001: m = mode & 1U ? 15U : 11U; break;
    case 0x010: m = 7U; break;
    case 0x011: m = 15U; break;
    case 0x100: m = mode & 1U ? 6U : 2U; break;
    case 0x101: m = mode & 1U ? 14U : 10U; break;
    case 0x110: m = 6U; break;
    case 0x111: m = 14U; break;
    case 0x200: m = mode & 1U ? 5U : 1U; break;
    case 0x201: m = mode & 1U ? 13U : 9U; break;
    case 0x210: m = 5U; break;
    case 0x211: m = 13U; break;
    case 0x300: m = mode & 1U ? 4U : 0U; break;
    case 0x301: m = mode & 1U ? 12U : 8U; break;
    case 0x310: m = 4U; break;
    case 0x311: m = 12U; break;
    default: {
        uint32_t diff = code - 0x311U;
        if (diff == 0xffcffU) m = 19U;
        else {
            diff -= 0xffcffU;
            if (diff == 1U) m = 15U;
            else if (diff == 0x100U) m = 18U;
            else if (diff == 0x101U) m = 14U;
            else if (diff == 0x200U) m = 17U;
            else if (diff == 0x201U) m = 13U;
            else if (diff == 0x300U) m = 16U;
            else if (diff == 0x301U) m = 12U;
            else return 5;
        }
        break;
    }
    }
    *major = m;

    uint32_t minor_code = flags & 0xff00fU;
    if (minor_code == 0U) *minor = 0U;
    else if (minor_code == 1U) *minor = mode & 1U ? 7U : 1U;
    else if (minor_code == 0x1000U || minor_code == 0x11000U) *minor = 2U;
    else if (minor_code == 0x1001U || minor_code == 0x11001U) *minor = 4U;
    else if (minor_code == 0x2000U || minor_code == 0x12000U) *minor = 3U;
    else if (minor_code == 0x2001U || minor_code == 0x12001U) *minor = 5U;
    else if (minor_code == 0x10000U) *minor = 6U;
    else if (minor_code == 0x10001U) *minor = 7U;
    else return 5;
    return 0;
}

/* Predicate at locked 0x41f3f0; independently exercised by the spot-handler
 * event comparison (72 cases). Keep its fixed-address reads explicit. */
static uint32_t native_spot_power_predicate_41f3f0(void)
{
    if (U8(0x200271bfU) == 0U) return 0U;
    uint32_t mode = U32(0x40008800U);
    if ((mode & 0x0fU) == 0U || (mode & 0x80000000U) != 0U) return 0U;
    return ((mode >> 30) & 1U) == 0U;
}

uint32_t native_spot_buck_deepsleep_scan(uint32_t snapshot[4], uint8_t temperature)
{
    if (temperature == 3U || (snapshot[0] & 0x3fffffffU) != 0U ||
        (snapshot[1] & 0x4c4U) != 0U ||
        (U32(0x400204d8U) & 0x20000000U) != 0U) {
        U8(0x200271c0U) = 1U;
        return 0U;
    }

    uint32_t power = U32(0x40008800U) & 0x0fU;
    if (native_spot_power_predicate_41f3f0() != 0U &&
        power != 0U && power <= 2U) {
        U8(0x200271c0U) = 1U;
        return 0U;
    }

    uint32_t active = U32(0x40008010U);
    for (uint32_t i = 0; i < 16U; ++i) {
        uint32_t channel = U32(0x40008200U + i * 0x20U);
        if ((channel & 1U) == 0U || ((active >> i) & 1U) == 0U) continue;
        uint32_t kind = (channel & 0x1ffffU) >> 8;
        if (kind < 6U || (kind >= 19U && kind <= 24U) ||
            (kind >= 256U && kind <= 479U)) {
            U8(0x200271c0U) = 1U;
            return 0U;
        }
    }
    U8(0x200271c0U) = 0U;
    return 0U;
}

extern uint32_t clock_request(uint32_t clock_id, uint32_t user_id);
extern uint32_t clock_release(uint32_t clock_id, uint32_t user_id);
extern void opencfw_bl_delay_us(uint32_t microseconds);

static void native_spot_delay_us(uint32_t microseconds)
{
    opencfw_bl_delay_us(microseconds);
}

void native_spot_trim_enable_42adb8(uint8_t enable)
{
    if (enable != 0U) {
        U32(0x400201b0U) |= 0x18000U;
        U32(0x40020088U) = (U32(0x40020088U) & 0xffffffc0U) |
                           ((U32(0x20026c08U) >> 14) & 0x3fU);
    }
    uint32_t old = U32(0x40020080U);
    uint32_t low = old & 0x3ffU;
    uint32_t correction = low + 7U < 0x400U ? 7U : 0x3ffU - low;
    U32(0x200270a4U) = correction;
    U32(0x40020080U) = (correction + old) & 0x3ffU | (old & 0xfffffc00U);
}

void native_spot_profile_trim_42ae24(uint8_t restore)
{
    U32(0x40020088U) = (U32(0x40020088U) & 0xffffffc0U) |
                        ((U32(0x20026c08U) >> 2) & 0x3fU);
    U32(0x400201b0U) = (U32(0x400201b0U) & 0xfffe7fffU) |
                        ((U32(0x20026c08U) & 3U) << 15);
    if (restore != 0U) {
        uint32_t old = U32(0x40020080U);
        U32(0x40020080U) = (old - U32(0x200270a4U)) & 0x3ffU |
                            (old & 0xfffffc00U);
    }
}

void native_spot_trim_restore_42ae6c(void)
{
    if (U8(0x200271aeU) == 0U) {
        U32(0x40020044U) = (U32(0x40020044U) & 0xffffff80U) |
                            (U32(0x200270a8U) & 0x7fU);
        U32(0x4002004cU) = (U32(0x4002004cU) & 0xffffff80U) |
                            (U32(0x200270acU) & 0x7fU);
    }
}

void native_spot_power_transition_trims(uint32_t new_minor, uint32_t new_major)
{
    uint32_t *const profile = (uint32_t *)(uintptr_t)0x20026ba0U;
    volatile uint32_t *const trim_a = (volatile uint32_t *)(uintptr_t)0x40020080U;
    volatile uint32_t *const trim_b = (volatile uint32_t *)(uintptr_t)0x40020088U;
    uint32_t a = *trim_a, b = *trim_b;
    uint32_t da = (a & 0x3ffU) + 14U < 0x400U ? 14U : 0x3ffU - (a & 0x3ffU);
    uint32_t db = (b & 0x3fU) + 6U < 0x40U ? 6U : 0x3fU - (b & 0x3fU);
    *trim_a = (da + a) & 0x3ffU | (a & 0xfffffc00U);
    *trim_b = (db + b) & 0x3fU | (b & 0xffffffc0U);
    native_spot_delay_us(20U);
    U32(0x40020380U) |= 0x20000000U;
    U32(0x40020380U) |= 0x10000000U;
    native_spot_delay_us(20U);

    uint32_t v0, v1;
    if (new_minor == 0U) {
        v0 = profile[0x5c / 4] & 0x1fU;
        v1 = (profile[0x5c / 4] & 0x7fffU) >> 10;
    } else if (new_minor == 2U) {
        v0 = profile[0x54 / 4] & 0x1fU;
        v1 = profile[0x58 / 4] & 0x1fU;
    } else if (new_minor < 2U) {
        uint32_t p = profile[0x5c / 4];
        v0 = (p & 0x3ffU) >> 5;
        v1 = (p & 0xfffffU) >> 15;
    } else if (new_minor == 4U) {
        v0 = (profile[0x54 / 4] & 0x3ffU) >> 5;
        v1 = (profile[0x58 / 4] & 0x3ffU) >> 5;
    } else if (new_minor < 4U) {
        v0 = (profile[0x54 / 4] & 0x7fffU) >> 10;
        v1 = (profile[0x58 / 4] & 0x7fffU) >> 10;
    } else if (new_minor == 6U) {
        v0 = profile[0x60 / 4] & 0x1fU;
        v1 = (profile[0x60 / 4] & 0x7fffU) >> 10;
    } else if (new_minor < 6U) {
        v0 = (profile[0x54 / 4] & 0xfffffU) >> 15;
        v1 = (profile[0x58 / 4] & 0xfffffU) >> 15;
    } else if (new_minor == 7U) {
        v0 = (U32(0x40020344U) & 0xffffU) >> 11;
        v1 = (U32(0x40020354U) & 0x3fffffU) >> 17;
    } else {
        v0 = (profile[0x54 / 4] & 0xfffffU) >> 15;
        v1 = (profile[0x58 / 4] & 0xfffffU) >> 15;
    }
    if (new_major == 8U)
        v0 = (profile[0x5c / 4] & 0x1ffffffU) >> 20;
    else if (new_major == 12U)
        v0 = (profile[0x54 / 4] & 0x1ffffffU) >> 20;
    else if (new_major == 14U)
        v0 = v0 + 6U < 0x20U ? v0 + 6U : 0x1fU;
    else if (new_major == 15U)
        v0 = v0 + 12U < 0x20U ? v0 + 12U : 0x1fU;

    U32(0x40020344U) = (U32(0x40020344U) & 0xc1ffffffU) | ((v0 & 0x1fU) << 25);
    U32(0x40020358U) = (U32(0x40020358U) & 0xffffe0ffU) | (v1 << 8);
    if (new_major == 1U || new_major == 5U || new_major == 17U)
        U32(0x4002034cU) = (U32(0x4002034cU) & 0xc1ffffffU) | 0x08000000U;
    else
        U32(0x4002034cU) = (U32(0x4002034cU) & 0xc1ffffffU) | 0x0c000000U;
    U32(0x40020380U) &= 0xdfffffffU;
    U32(0x40020380U) &= 0xefffffffU;
    a = *trim_a;
    b = *trim_b;
    *trim_a = (a - da) & 0x3ffU | (a & 0xfffffc00U);
    *trim_b = (b - db) & 0x3fU | (b & 0xffffffc0U);
}

static void native_spot_register_barrier(void)
{
    __asm volatile("dsb sy\n\tisb sy" ::: "memory");
}

static uint32_t native_spot_flush_disable(void)
{
    uint32_t result = (U32(0xe001e300U) & 0x300U) == 0U;
    if (result != 0U) {
        native_spot_register_barrier();
        U32(0xe000ed14U) &= ~0x20000U;
        U32(0xe000ef50U) = 0U;
        native_spot_register_barrier();
    }
    return result == 0U;
}

static uint32_t native_spot_flush_enable(void)
{
    uint32_t result = (U32(0xe001e300U) & 0x300U) == 0U;
    if (result != 0U) {
        native_spot_register_barrier();
        U32(0xe000ef50U) = 0U;
        native_spot_register_barrier();
        U32(0xe000ed14U) |= 0x20000U;
        native_spot_register_barrier();
    }
    return result == 0U;
}

static void native_spot_clock_ramp_enable(uint32_t wait)
{
    (void)clock_request(4U, 0x31U);
    U32(0x400083e8U) = wait * 6U;
    U32(0x40008010U) |= 0x8000U;
    U32(0x400083e0U) |= 2U;
    U32(0x400083e0U) &= ~2U;
    U32(0xe000e108U) = 0x40000U;
    U32(0x400083e0U) |= 1U;
}

static void native_spot_clock_ramp_disable(uint32_t wait)
{
    U32(0x400083e0U) &= ~1U;
    U32(0x400083e0U) |= 2U;
    U32(0x400083e0U) &= ~2U;
    U32(0x400083e8U) = wait * 6U;
    U32(0x40008068U) = 0xc0000000U;
    U32(0xe000e288U) = 0x40000U;
    U32(0x400083e0U) |= 1U;
}

static void native_spot_clock_transition_release(void)
{
    U32(0x400083e0U) &= ~1U;
    U32(0x40008010U) &= ~0x8000U;
    (void)clock_release(4U, 0x31U);
    U32(0xe000e188U) = 0x40000U;
    U32(0x40008068U) = 0xc0000000U;
    (void)U32(0x47ff0000U);
    U32(0xe000e288U) = 0x40000U;
}

uint32_t native_spot_state_transition(uint32_t new_major, uint32_t old_major,
                                      uint32_t new_minor, uint32_t old_minor)
{
    volatile uint32_t *const profile = (volatile uint32_t *)(uintptr_t)0x20026ba0U;
    volatile uint32_t *const major_rank = (volatile uint32_t *)(uintptr_t)0x200000a4U;
    volatile uint32_t *const minor_rank = (volatile uint32_t *)(uintptr_t)0x200000f4U;
    volatile uint32_t *const current_index = (volatile uint32_t *)(uintptr_t)0x20000148U;
    volatile uint32_t *const misc = (volatile uint32_t *)(uintptr_t)0x400083e0U;
    volatile uint32_t *const bus_trim = (volatile uint32_t *)(uintptr_t)0x40020080U;
    volatile uint32_t *const trim_delta_a = (volatile uint32_t *)(uintptr_t)0x200270a4U;
    volatile uint32_t *const trim_delta_b = (volatile uint32_t *)(uintptr_t)0x200270a8U;
    uint32_t old_entry = profile[old_major + 1U];
    uint32_t new_entry = profile[new_major + 1U];
    uint32_t current_entry = profile[*current_index + 1U];
    uint32_t lower = major_rank[old_major] < major_rank[new_major] ||
                     minor_rank[old_major] < minor_rank[new_major];
    uint32_t special = new_minor != old_minor || old_major == 1U ||
        old_major == 5U || old_major == 17U || old_major == 8U ||
        old_major == 12U || old_major == 14U || old_major == 15U ||
        new_major == 1U || new_major == 5U || new_major == 17U ||
        new_major == 8U || new_major == 12U || new_major == 14U ||
        new_major == 15U;
    uint32_t syspll = *misc & 1U;
    if (new_major == old_major) {
        if (new_minor != old_minor)
            native_spot_power_transition_trims(new_minor, new_major);
        return old_minor;
    }
    if (lower) {
        if (special) native_spot_power_transition_trims(new_minor, new_major);
        U32(0x200270a8U) = (new_entry & 0x0fffffffU) >> 21;
        U32(0x200270acU) = new_entry & 0x7fU;
        U32(0x40020080U) = (U32(0x40020080U) & 0xffffc3ffU) |
                            (((new_entry & 0x1fffffU) >> 17) << 10);
        if (syspll != 0U) {
            uint32_t v = (new_entry & 0x1ffffU) >> 7;
            uint32_t delta = v + 7U < 0x400U ? 7U : 0x3ffU - v;
            *trim_delta_a = delta;
            *bus_trim = (delta + (new_entry >> 7)) & 0x3ffU |
                         (*bus_trim & 0xfffffc00U);
            old_entry = current_entry;
        } else {
            *bus_trim = (new_entry & 0x1ffffU) >> 7 |
                         (*bus_trim & 0xfffffc00U);
            old_entry = profile[old_major + 1U];
        }
        uint32_t target_v = (new_entry & 0x0fffffffU) >> 21;
        uint32_t current_v = (old_entry & 0x0fffffffU) >> 21;
        int32_t step_v = current_v < target_v ?
                         (int32_t)((target_v - current_v) * 2U) :
                         -(int32_t)(current_v - target_v);
        uint32_t target_c = new_entry & 0x7fU;
        uint32_t current_c = old_entry & 0x7fU;
        int32_t step_c = current_c < target_c ?
                         (int32_t)((target_c - current_c) * 2U) :
                         -(int32_t)(current_c - target_c);
        uint32_t ramp = (uint32_t)(step_v + (int32_t)current_v) < 0x80U &&
                        (uint32_t)(step_c + (int32_t)current_c) < 0x80U &&
                        U8(0x200271aeU) == 0U;
        if (ramp != 0U) {
            U32(0x40020044U) = (U32(0x40020044U) & 0xffffff80U) |
                                ((uint32_t)(step_v + (int32_t)current_v) & 0x7fU);
            U32(0x4002004cU) = (U32(0x4002004cU) & 0xffffff80U) |
                                ((uint32_t)(step_c + (int32_t)current_c) & 0x7fU);
        } else {
            U32(0x40020044U) = (U32(0x40020044U) & 0xffffff80U) | target_v;
            U32(0x4002004cU) = (U32(0x4002004cU) & 0xffffff80U) | target_c;
        }
        uint32_t wait = ramp != 0U ? 50U : (U8(0x200271aeU) == 0U ? 200U : 2000U);
        if (syspll != 0U) {
            native_spot_clock_ramp_disable(wait);
        } else {
            native_spot_trim_enable_42adb8(1U);
            native_spot_clock_ramp_enable(wait);
            *current_index = old_major;
        }
        if ((old_major < 8U || (old_major >= 16U && old_major < 20U)) &&
            new_major >= 8U && new_major < 16U) {
            if ((U32(0xe000ed14U) & 0x20000U) != 0U) {
                (void)native_spot_flush_disable();
                U32(0x4002037cU) |= 0x10000U;
                U8(0x200271b2U) = 1U;
                native_spot_delay_us(20U);
                (void)native_spot_flush_enable();
            } else {
                U32(0x4002037cU) |= 0x10000U;
                U8(0x200271b2U) = 1U;
                native_spot_delay_us(20U);
            }
        } else {
            native_spot_delay_us(20U);
        }
        (void)wait;
    } else {
        uint32_t current_is_lower = syspll != 0U &&
            (major_rank[*current_index] < major_rank[new_major] ||
             minor_rank[*current_index] < minor_rank[new_major]);
        uint32_t v = (new_entry & 0x1ffffU) >> 7;
        if (current_is_lower != 0U) {
            uint32_t delta = v + 7U < 0x400U ? 7U : 0x3ffU - v;
            *trim_delta_a = delta;
            *bus_trim = (delta + (new_entry >> 7)) & 0x3ffU |
                         (*bus_trim & 0xfffffc00U);
        } else {
            *bus_trim = v | (*bus_trim & 0xfffffc00U);
        }
        *bus_trim = (*bus_trim & 0xffffc3ffU) |
                    (((new_entry & 0x1fffffU) >> 17) << 10);
        if (U8(0x200271aeU) == 0U && syspll != 0U) {
            *trim_delta_b = (new_entry & 0x0fffffffU) >> 21;
            U32(0x200270acU) = new_entry & 0x7fU;
        } else {
            U32(0x40020044U) = (U32(0x40020044U) & 0xffffff80U) |
                                ((new_entry & 0x0fffffffU) >> 21);
            U32(0x4002004cU) = (U32(0x4002004cU) & 0xffffff80U) |
                                (new_entry & 0x7fU);
        }
        if (special) native_spot_power_transition_trims(new_minor, new_major);
        uint32_t current_lower = syspll != 0U &&
            major_rank[new_major] <= major_rank[*current_index] &&
            minor_rank[new_major] <= minor_rank[*current_index];
        if (current_lower != 0U) {
            native_spot_clock_transition_release();
            native_spot_trim_restore_42ae6c();
            native_spot_profile_trim_42ae24(0U);
        }
    }
    return old_minor;
}
