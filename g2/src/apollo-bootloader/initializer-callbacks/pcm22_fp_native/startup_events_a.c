/* SPDX-License-Identifier: MIT
 * Fixed-address C reconstruction of locked SPOT callback 0x42A878.
 * Native helper closure is bounded by the installed-callback tests.
 */
#include "startup_events_a.h"
#include <stddef.h>

#define R32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define R8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
#define W8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))

extern uint32_t opencfw_boot_control_critical_save(void);
extern void event_a_power_trims_update(uint32_t new_major, uint32_t old_major,
                                       uint32_t new_minor, uint32_t old_minor);

_Static_assert(offsetof(startup_events_a_snapshot, temperature_class) == 0x10,
               "locked local byte offset");
_Static_assert(offsetof(startup_events_a_snapshot, cpu_state) == 0x11,
               "locked local byte offset");
_Static_assert(offsetof(startup_events_a_snapshot, gpu_state) == 0x12,
               "locked local byte offset");

/* Recovered call-free leaves. The classifier thresholds are authenticated
 * literals in the original 0x427E0C body. */
/* Preserve scalar VCMP exception/control behavior, including sNaN IOC and
 * FZ input-denormal IDC. Read flags; do not write/normalize FPSCR. */
static uint32_t event_a_f32_compare_flags(uint32_t left,uint32_t right)
{
 uint32_t flags;
 __asm__ volatile("vmov s0,%1; vmov s1,%2; vcmp.f32 s0,s1; vmrs %0,fpscr"
                  : "=r"(flags) : "r"(left),"r"(right) : "s0","s1","cc");
 return flags;
}
static bool event_a_fp_negative(uint32_t f){return (f&0x80000000u)!=0;}
static bool event_a_fp_blt(uint32_t f){return ((f>>31)^ (f>>28))&1u;}
NI uint32_t event_a_temperature_classify_bits(uint32_t bits)
{
 uint32_t f=event_a_f32_compare_flags(bits,0xc1a00000u);
 if(event_a_fp_negative(f)){
  f=event_a_f32_compare_flags(bits,0xc3888000u);
  if(!event_a_fp_blt(f))return 0;
 }
 f=event_a_f32_compare_flags(bits,0xc1a00000u);
 if(!event_a_fp_blt(f)){
  f=event_a_f32_compare_flags(bits,0);
  if(event_a_fp_negative(f))return 1;
 }
 f=event_a_f32_compare_flags(bits,0);
 if(!event_a_fp_blt(f)){
  f=event_a_f32_compare_flags(bits,0x42480000u);
  if(event_a_fp_negative(f))return 2;
 }
 f=event_a_f32_compare_flags(bits,0x42480000u);
 if(!event_a_fp_blt(f)){
  f=event_a_f32_compare_flags(bits,0x447a0000u);
  if(event_a_fp_negative(f))return 3;
 }
 return 4;
}

NI void event_a_internal_power_domain(uint8_t requested, uint8_t current)
{
    if (current == 1U && requested == 2U) W8(0x200271b0U) = 1U;
}

static bool event_a_sleep_mode_allows(void)
{
    const uint32_t mode = R32(0x40008800U);
    if (R8(0x200271bfU) == 0U || (mode & 0x0fU) == 0U ||
        (mode & 0x80000000U) != 0U) return false;
    return (mode & 0x40000000U) == 0U;
}

NI void event_a_deepsleep_state(startup_events_a_snapshot *s)
{
    uint32_t mode, enabled;
    if (s->temperature_class == 3U ||
        (s->device_power & 0x3fffffffU) != 0U ||
        (s->audio_power & 0x4c4U) != 0U ||
        (R32(0x400204d8U) & 0x20000000U) != 0U) {
        W8(0x200271c0U) = 1U;
        return;
    }
    mode = R32(0x40008800U);
    if (event_a_sleep_mode_allows() && (mode & 0x0fU) >= 1U &&
        (mode & 0x0fU) <= 2U) {
        W8(0x200271c0U) = 1U;
        return;
    }
    enabled = R32(0x40008010U);
    for (uint32_t slot = 0U; slot < 16U; ++slot) {
        const uint32_t descriptor = R32(0x40008200U + slot * 0x20U);
        uint32_t kind;
        if ((descriptor & 1U) == 0U ||
            ((enabled >> slot) & 1U) == 0U) continue;
        kind = (descriptor & 0x1ffffU) >> 8;
        if (kind < 6U || (kind >= 0x13U && kind <= 0x18U) ||
            (kind >= 0x100U && kind <= 0x1dfU)) {
            W8(0x200271c0U) = 1U;
            return;
        }
    }
    W8(0x200271c0U) = 0U;
}

NI uint32_t event_a_state_determine(const startup_events_a_snapshot *s,
                                      uint32_t *major, uint32_t *minor)
{
    /* The original 0x434168 lookup cell in the locked image contains zero. */
    uint32_t state = 0U;
    uint32_t cpu_active;
    uint32_t dev_bits = s->device_power & 0x3fffffffU;
    uint32_t audio_active = s->audio_power & 0x4c4U;
    uint32_t gpu = (uint8_t)s->gpu_state;
    uint32_t major_code, minor_code;
    const uint32_t cpu_state = (uint8_t)s->cpu_state;
    const uint32_t temp = s->temperature_class & 0x0fU;
    const bool peripheral_active = dev_bits != 0U || audio_active != 0U;

    if (cpu_state == 1U) cpu_active = 1U;
    else if (cpu_state == 0U) cpu_active = 0U;
    else cpu_active = (R32(0x40021000U) & 3U) == 2U ? 1U : 0U;
    state |= (temp << 8) | cpu_active;

    if (gpu == 1U || gpu == 2U || peripheral_active) state |= 0x10U;
    if (gpu == 1U || gpu == 2U) state |= (gpu & 0x0fU) << 12;
    if (peripheral_active) state |= 0x10000U;
    if (gpu == 1U || gpu == 2U || (dev_bits & 0x00c00000U) != 0U)
        state |= 0x00100000U;

    major_code = state & 0x00f00fffU;
    switch (major_code) {
    case 0x00000000U: *major = (R8(0x2002708cU) & 1U) ? 7U : 3U; break;
    case 0x00000001U: *major = (R8(0x2002708cU) & 1U) ? 15U : 11U; break;
    case 0x00000010U: *major = 7U; break;
    case 0x00000011U: *major = 15U; break;
    case 0x00000100U: *major = (R8(0x2002708cU) & 1U) ? 6U : 2U; break;
    case 0x00000101U: *major = (R8(0x2002708cU) & 1U) ? 14U : 10U; break;
    case 0x00000110U: *major = 6U; break;
    case 0x00000111U: *major = 14U; break;
    case 0x00000200U: *major = (R8(0x2002708cU) & 1U) ? 5U : 1U; break;
    case 0x00000201U: *major = (R8(0x2002708cU) & 1U) ? 13U : 9U; break;
    case 0x00000210U: *major = 5U; break;
    case 0x00000211U: *major = 13U; break;
    case 0x00000300U: *major = (R8(0x2002708cU) & 1U) ? 4U : 0U; break;
    case 0x00000301U: *major = (R8(0x2002708cU) & 1U) ? 12U : 8U; break;
    case 0x00000310U: *major = 4U; break;
    case 0x00000311U: *major = 12U; break;
    case 0x00100010U: *major = 19U; break;
    case 0x00100011U: *major = 15U; break;
    case 0x00100110U: *major = 18U; break;
    case 0x00100111U: *major = 14U; break;
    case 0x00100210U: *major = 17U; break;
    case 0x00100211U: *major = 13U; break;
    case 0x00100310U: *major = 16U; break;
    case 0x00100311U: *major = 12U; break;
    default: return 5U;
    }

    minor_code = state & 0x000ff00fU;
    switch (minor_code) {
    case 0x00000000U: *minor = 0U; break;
    case 0x00000001U: *minor = (R8(0x2002708cU) & 1U) ? 7U : 1U; break;
    case 0x00001000U: *minor = 2U; break;
    case 0x00001001U: *minor = 4U; break;
    case 0x00002000U: *minor = 3U; break;
    case 0x00002001U: *minor = 5U; break;
    case 0x00010000U: *minor = 6U; break;
    case 0x00010001U: *minor = 7U; break;
    case 0x00011000U: *minor = 2U; break;
    case 0x00011001U: *minor = 4U; break;
    case 0x00012000U: *minor = 3U; break;
    case 0x00012001U: *minor = 5U; break;
    default: return 5U;
    }
    return 0U;
}

NI uint32_t opencfw_boot_spotmgr_power_state_update_a(
    uint32_t stimulus, uint32_t on, void *opaque_args)
{
    uint32_t status = 0U;
    uint32_t new_major = 0U, new_minor = 0U;
    uint32_t irq;
    uint8_t skip_update = 0U;
    uint8_t skip_decode = 1U;
    uint8_t *args = (uint8_t *)opaque_args;
    startup_events_a_snapshot snapshot;

    if (((R32(0x40021108U) & 0x3fU) >> 4) != 3U) return 0U;
    if (R32(0x20026ba0U) != 0x1f01600dU) return 1U;

    irq = opencfw_boot_control_critical_save();
    if ((uint8_t)stimulus == AM_HAL_SPOTMGR_STIM_CPU_STATE && args != NULL) {
        const uint8_t requested = args[0];
        const uint8_t current = R8(0x200271beU);
        if ((current == 4U || current == 3U || current == 2U) &&
            (requested == 0U || requested == 1U)) {
            skip_update = 1U;
            W8(0x200271beU) = requested;
        }
    }

    if (!skip_update) {
        snapshot.device_power = R32(0x40021008U);
        snapshot.audio_power = R32(0x40021010U);
        snapshot.memory_power = R32(0x40021018U);
        snapshot.ssram_power = R32(0x40021028U);
        snapshot.temperature_class = R8(0x200271bdU);
        if ((snapshot.device_power & 0x00040000U) != 0U)
            snapshot.gpu_state = R8(0x200271a5U) == 0U ? 1 : 2;
        else
            snapshot.gpu_state = 0;
        snapshot.cpu_state = (int8_t)R8(0x200271beU);

        if ((uint8_t)stimulus == AM_HAL_SPOTMGR_STIM_CPU_STATE) {
            if (args == NULL) {
                status = 6U;
            } else {
                const uint8_t requested = args[0];
                snapshot.cpu_state = (int8_t)requested;
                if (R8(0x200271beU) != requested) {
                    if (requested == 2U) {
                        event_a_deepsleep_state(&snapshot);
                        const uint32_t current_mode = R32(0x20000150U);
                        W8(0x200271afU) =
                            (current_mode >= 9U && current_mode <= 11U &&
                             R8(0x2000055aU) != 7U) ? 1U : 0U;
                    }
                    if (R8(0x200271beU) == 0U && requested == 1U) {
                        W8(0x200271beU) = 1U;
                    } else if (R8(0x200271beU) == 1U && requested == 0U) {
                        W8(0x200271beU) = 0U;
                    } else if (R8(0x200271beU) == 0U && requested == 2U) {
                        W8(0x200271beU) = 2U;
                    } else {
                        event_a_internal_power_domain(requested,
                                                      R8(0x200271beU));
                        W8(0x200271beU) = requested;
                        skip_decode = 0U;
                    }
                    snapshot.cpu_state = (int8_t)requested;
                }
            }
        } else if ((uint8_t)stimulus == AM_HAL_SPOTMGR_STIM_TEMP) {
            if (args == NULL) {
                status = 6U;
            } else {
                const uint32_t temperature_bits = *(uint32_t *)(void *)args;
                snapshot.temperature_class = (uint8_t)
                    event_a_temperature_classify_bits(temperature_bits);
                W8(0x200271bdU) = snapshot.temperature_class;
                W8(0x20000553U) = snapshot.temperature_class < 3U ? 1U : 0U;
                if (snapshot.temperature_class == 0U) {
                    *(uint32_t *)(void *)(args + 4) = 0xc3888000U;
                    *(uint32_t *)(void *)(args + 8) = 0xc1a00000U;
                } else if (snapshot.temperature_class == 2U) {
                    *(uint32_t *)(void *)(args + 4) = 0xc0000000U;
                    *(uint32_t *)(void *)(args + 8) = 0x42480000U;
                } else if (snapshot.temperature_class < 2U) {
                    *(uint32_t *)(void *)(args + 4) = 0xc1b00000U;
                    *(uint32_t *)(void *)(args + 8) = 0U;
                } else if (snapshot.temperature_class == 4U) {
                    *(uint32_t *)(void *)(args + 4) = 0U;
                    *(uint32_t *)(void *)(args + 8) = 0U;
                    status = 6U;
                } else {
                    *(uint32_t *)(void *)(args + 4) = 0x42400000U;
                    *(uint32_t *)(void *)(args + 8) = 0x447a0000U;
                }
            }
        } else if ((uint8_t)stimulus < AM_HAL_SPOTMGR_STIM_TEMP) {
            if (args == NULL) status = 6U;
            else snapshot.gpu_state = (int8_t)args[0];
        } else if ((uint8_t)stimulus == AM_HAL_SPOTMGR_STIM_AUDSSPWR) {
            if (on) {
                if (args == NULL) status = 6U;
                else snapshot.audio_power |= *(uint32_t *)(void *)args;
            }
        } else if ((uint8_t)stimulus < AM_HAL_SPOTMGR_STIM_AUDSSPWR) {
            if (on) {
                if (args == NULL) status = 6U;
                else snapshot.device_power |= *(uint32_t *)(void *)args;
            }
        } else if ((uint8_t)stimulus == AM_HAL_SPOTMGR_STIM_SSRAMPWR) {
            if (on) {
                if (args == NULL) status = 6U;
                else snapshot.ssram_power = *(uint32_t *)(void *)args;
            }
        } else if ((uint8_t)stimulus < AM_HAL_SPOTMGR_STIM_SSRAMPWR) {
            if (args == NULL) status = 6U;
            else snapshot.memory_power = *(uint32_t *)(void *)args;
        } else {
            status = 6U;
        }

        if (status == 0U && skip_decode) {
            status = event_a_state_determine(&snapshot, &new_major, &new_minor);
            if (status == 0U) {
                const uint32_t old_major = R32(0x20000150U);
                const uint32_t old_minor = R32(0x200001c4U);
                if (new_major != old_major || new_minor != old_minor)
                    event_a_power_trims_update(new_major, old_major,
                                               new_minor, old_minor);
                W32(0x20000150U) = new_major;
                W32(0x200001c4U) = new_minor;
            }
        }
    }

    __asm__ volatile("msr primask, %0" :: "r"(irq) : "memory");
    return status;
}
