/* SPDX-License-Identifier: MIT
 * Fixed-address C hypothesis for locked SPOT callback 0x42ba00.
 * Lower calls route through isolated providers; the verified temperature,
 * scanner, transition-effect, decoder, and state-transition bodies execute as
 * compiled source reconstructions in the native comparison build.
 * This file is not firmware integration.
 */
#include <stdint.h>

#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define U8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))

extern uint32_t opencfw_boot_control_critical_save(void);
extern uint8_t event_child_temperature_range(float value);
extern void event_child_buck_deepsleep_scan(uint32_t snapshot[4],
                                             uint8_t temperature_category);
extern void event_child_transition_effect(uint8_t requested, uint8_t current);
extern int event_child_state_decode(const uint32_t snapshot[4],
                                    uint8_t temperature_category,
                                    uint8_t state, uint8_t auxiliary_category,
                                    uint32_t *major, uint32_t *minor);
extern void event_child_state_transition(uint32_t new_major,
                                         uint32_t old_major,
                                         uint32_t new_minor,
                                         uint32_t old_minor);

/* ABI observed at table slot +4: R0 stimulus, R1 on/off, R2 argument pointer. */
NI uint32_t opencfw_boot_spot_state_power_event(uint8_t stimulus,
                                                uint8_t on,
                                                uint32_t *args)
{
    uint32_t status = 0;
    uint32_t decoded_major = 0;
    uint32_t decoded_minor = 0;
    uint8_t deferred_current_effect = 0;
    uint8_t skip_decode = 0;
    uint8_t shortcut = 0;
    uint8_t category;
    uint8_t current;
    uint8_t requested;
    uint8_t temp_category;
    uint8_t aux_category;
    uint32_t snapshot[4];
    uint32_t irq;

    /* Clock/peripheral-ready gate and the initialized-profile marker. */
    if (((U32(0x40021108U) & 0x3fU) >> 4) != 3U) return 0;
    if (U32(0x20026ba0U) != 0x1f01600dU) return 1;
    irq = opencfw_boot_control_critical_save();

    current = U8(0x200271bbU);
    if (stimulus == 0U && args != 0) {
        requested = (uint8_t)*args;
        category = current;
        if ((category == 4U || category == 3U || category == 2U) &&
            (requested == 0U || requested == 1U)) {
            shortcut = 1U;
            U8(0x200271bbU) = requested;
        }
    }

    if (!shortcut) {
        snapshot[0] = U32(0x40021008U);
        snapshot[1] = U32(0x40021010U);
        snapshot[2] = U32(0x40021018U);
        snapshot[3] = U32(0x40021028U);
        temp_category = U8(0x200271baU);
        if ((snapshot[0] & 0x00040000U) != 0U)
            aux_category = U8(0x200271a5U) == 0U ? 1U : 2U;
        else
            aux_category = 0U;
        requested = U8(0x200271bbU);

        if (stimulus == 0U) {
            if (args == 0) {
                status = 6U;
            } else {
                requested = (uint8_t)*args;
                if (U8(0x200271bbU) != requested) {
                    if (requested == 2U) {
                        event_child_buck_deepsleep_scan(snapshot, temp_category);
                        U8(0x200271afU) =
                            (U32(0x20000144U) == 8U || U32(0x20000144U) == 12U)
                            ? 0U : 1U;
                    }
                    if (U8(0x200271bbU) == 0U && requested == 1U) {
                        U8(0x200271bbU) = 1U;
                    } else if (U8(0x200271bbU) == 1U && requested == 0U) {
                        deferred_current_effect = 1U;
                    } else if (U8(0x200271bbU) == 0U && requested == 2U) {
                        if ((U8(0x2002708cU) & 1U) != 0U &&
                            aux_category != 1U && aux_category != 2U &&
                            (snapshot[0] & 0x3fffffffU) == 0U &&
                            (snapshot[1] & 0x4c4U) == 0U)
                            U8(0x200271afU) = 1U;
                        U8(0x200271bbU) = 2U;
                    } else {
                        event_child_transition_effect(requested,
                                                      U8(0x200271bbU));
                        U8(0x200271bbU) = requested;
                        skip_decode = 1U;
                    }
                }
            }
        } else if (stimulus == 2U) {
            if (args == 0) {
                status = 6U;
            } else {
                union { uint32_t word; float value; } temperature;
                temperature.word = *args;
                temp_category = event_child_temperature_range(temperature.value);
                U8(0x200271baU) = temp_category;
                U8(0x20000553U) = temp_category < 3U ? 1U : 0U;
                if (temp_category == 0U) {
                    args[1] = 0xc3888000U; args[2] = 0xc1a00000U;
                } else if (temp_category == 2U) {
                    args[1] = 0xc0000000U; args[2] = 0x42480000U;
                } else if (temp_category < 2U) {
                    args[1] = 0xc1b00000U; args[2] = 0U;
                } else if (temp_category == 4U) {
                    args[1] = 0U; args[2] = 0U; status = 6U;
                } else if (temp_category < 4U) {
                    args[1] = 0x42400000U; args[2] = 0x447a0000U;
                }
            }
        } else if (stimulus < 2U) {
            if (args == 0) status = 6U;
            else aux_category = (uint8_t)*args;
        } else if (stimulus == 4U) {
            if (on != 0U) {
                if (args == 0) status = 6U;
                else snapshot[1] |= *args;
            }
        } else if (stimulus < 4U) {
            if (on != 0U) {
                if (args == 0) status = 6U;
                else snapshot[0] |= *args;
            }
        } else if (stimulus == 6U) {
            if (on != 0U) {
                if (args == 0) status = 6U;
                else snapshot[3] = *args;
            }
        } else if (stimulus < 6U) {
            if (args == 0) status = 6U;
            else snapshot[2] = *args;
        } else {
            status = 6U;
        }

        if (status == 0U && !skip_decode) {
            status = (uint32_t)event_child_state_decode(snapshot,
                                                        temp_category,
                                                        requested,
                                                        aux_category,
                                                        &decoded_major,
                                                        &decoded_minor);
            if (status == 0U) {
                uint32_t old_major = U32(0x20000144U);
                uint32_t old_minor = U32(0x2000014cU);
                if ((decoded_major != old_major || decoded_minor != old_minor)) {
                    event_child_state_transition(decoded_major, old_major,
                                                 decoded_minor, old_minor);
                    if (deferred_current_effect) {
                        event_child_transition_effect(requested,
                                                      U8(0x200271bbU));
                        U8(0x200271bbU) = requested;
                    }
                }
                if ((old_major == 12U && decoded_major >= 13U && decoded_major <= 15U) ||
                    (old_major == 8U && decoded_major >= 9U && decoded_major <= 11U)) {
                    U32(0x4002037cU) |= 0x40U;
                    U32(0x4002037cU) |= 0x08U;
                }
                U32(0x20000144U) = decoded_major;
                U32(0x2000014cU) = decoded_minor;
            }
        }
    }

    __asm__ volatile("msr primask, %0" :: "r"(irq) : "memory");
    return status;
}
