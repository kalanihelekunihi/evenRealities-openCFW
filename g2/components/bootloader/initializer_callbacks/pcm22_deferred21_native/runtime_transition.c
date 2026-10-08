/* SPDX-License-Identifier: MIT. Reconstructed source for stock 0x41b954. */
#include "runtime_transition.h"
#include <stddef.h>

#define BOOT_CONTROL_HOOKS 0x20026e38u

extern uint32_t opencfw_boot_control_critical_save(void);
extern void opencfw_boot_control_delay_us(uint32_t microseconds);
extern uint32_t opencfw_boot_control_delay_status_change(
    uint32_t timeout, volatile uint32_t *address, uint32_t mask,
    uint32_t expected);

static uint32_t mode_config_hook(uint32_t arg0, uint32_t arg1, void *arg2)
{
    typedef uint32_t (*hook_t)(uint32_t, uint32_t, void *);
    hook_t hook = (hook_t)(uintptr_t)
        *(volatile uint32_t *)(uintptr_t)(BOOT_CONTROL_HOOKS + 4u);
    return hook != NULL ? hook(arg0, arg1, arg2) : 0u;
}

extern uint32_t opencfw_boot_startup_hook28(void);
static uint32_t mode_notify_hook(void) { return opencfw_boot_startup_hook28(); }

static void restore_primask(uint32_t value)
{
    __asm volatile("msr primask, %0" :: "r"(value) : "memory");
}

uint32_t opencfw_boot_control_transition(uint32_t mode)
{
    volatile uint32_t *const power_mode =
        (volatile uint32_t *)(uintptr_t)0x40021000u;
    volatile uint8_t *const saved_mode =
        (volatile uint8_t *)(uintptr_t)0x20000552u;
    volatile uint32_t *const wake_control =
        (volatile uint32_t *)(uintptr_t)0x40004044u;
    volatile uint32_t *const wake_status =
        (volatile uint32_t *)(uintptr_t)0x40004030u;
    const uint32_t previous = opencfw_boot_control_critical_save();
    const uint8_t selected = (uint8_t)mode;
    uint32_t result = 4u;

    if (selected == 2u) {
        uint8_t request = 1u;
        (void)mode_config_hook(0u, 0u, &request);
        const uint32_t waking = (*wake_control & (1u << 5)) == 0u;
        if (waking) {
            *wake_control |= 1u << 5;
            opencfw_boot_control_delay_us(1u);
            (void)opencfw_boot_control_delay_status_change(
                0x0fu, wake_status, 0x01000000u, 0x01000000u);
        }
        if ((*wake_status & 0x01000000u) != 0u) {
            *power_mode = (*power_mode & ~3u) | (selected & 3u);
            for (uint32_t count = 0u; count < 20u; ++count) {
                if ((*power_mode & 4u) != 0u) {
                    result = 0u;
                    break;
                }
                opencfw_boot_control_delay_us(1u);
            }
        } else {
            result = 1u;
        }
        if (waking)
            *wake_control &= ~0x20u;
        (void)mode_notify_hook();
    } else {
        *power_mode = (*power_mode & ~3u) | (selected & 3u);
        for (uint32_t count = 0u; count < 20u; ++count) {
            if ((*power_mode & 4u) != 0u) {
                result = 0u;
                break;
            }
            opencfw_boot_control_delay_us(1u);
        }
    }

    if (result == 0u) {
        *saved_mode = selected;
        if (selected != 2u) {
            uint8_t disabled = 0u;
            (void)mode_config_hook(0u, 0u, &disabled);
        }
    } else if (selected == 2u) {
        uint8_t disabled = 0u;
        (void)mode_config_hook(0u, 0u, &disabled);
    }
    restore_primask(previous);
    return result;
}
