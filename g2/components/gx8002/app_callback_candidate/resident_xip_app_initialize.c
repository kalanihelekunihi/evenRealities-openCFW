/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x10208cd4 application initialization plus its three local
 * callback bodies 0x10208c7c/98/a0. Product application-ops pointer at
 * 0x20026d38 is a runtime input; no default callback is synthesized.
 */
#include <stdint.h>

extern void gx8002_xip_queue_initialize_10206f9c(
    volatile uint32_t *, uint32_t, int32_t, int32_t);
extern uint32_t gx8002_xip_register_suspend_102076c0(const void *);
extern uint32_t gx8002_xip_register_resume_10207718(const void *);
extern void gx8002_xip_watchdog_initialize_10206720(
    uint32_t, uint32_t, void (*)(void), uint32_t);
extern void gx8002_xip_watchdog_stop_102067ac(void);
extern void gx8002_xip_reboot_102067b8(void);

struct gx8002_xip_named_callback {
    void *callback;
    const char *name;
};
_Static_assert(sizeof(struct gx8002_xip_named_callback) == 8,
               "native named callback ABI");

static volatile uint32_t *const app_ops_slot =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20026d38);

uint32_t gx8002_xip_app_resume_10208c7c(void)
{
    uint32_t raw = *app_ops_slot;
    if (raw != 0u) {
        volatile uint32_t *ops = (volatile uint32_t *)(uintptr_t)raw;
        uint32_t callback = ops[0x18u / 4u];
        if (callback != 0u)
            ((void (*)(uint32_t))(uintptr_t)callback)(ops[0x1cu / 4u]);
    }
    return 0u;
}

void gx8002_xip_app_watchdog_callback_10208c98(void)
{
    gx8002_xip_reboot_102067b8();
}

uint32_t gx8002_xip_app_suspend_10208ca0(void)
{
    gx8002_xip_watchdog_stop_102067ac();
    uint32_t raw = *app_ops_slot;
    if (raw != 0u) {
        volatile uint32_t *ops = (volatile uint32_t *)(uintptr_t)raw;
        uint32_t callback = ops[0x10u / 4u];
        if (callback != 0u)
            ((void (*)(uint32_t))(uintptr_t)callback)(ops[0x14u / 4u]);
    }
    return 0u;
}

uint32_t gx8002_xip_app_initialize_10208cd4(void)
{
    gx8002_xip_queue_initialize_10206f9c(
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002ecd8),
        UINT32_C(0x2002e880), 64, 8);
    uint32_t raw = *app_ops_slot;
    if (raw != 0u) {
        volatile uint32_t *ops = (volatile uint32_t *)(uintptr_t)raw;
        uint32_t callback = ops[1];
        if (callback != 0u)
            ((void (*)(uint32_t))(uintptr_t)callback)(callback);
    }
    const struct gx8002_xip_named_callback suspend = {
        (void *)(uintptr_t)gx8002_xip_app_suspend_10208ca0,
        "_LvpAppSuspend",
    };
    const struct gx8002_xip_named_callback resume = {
        (void *)(uintptr_t)gx8002_xip_app_resume_10208c7c,
        "_LvpAppResume",
    };
    (void)gx8002_xip_register_suspend_102076c0(&suspend);
    (void)gx8002_xip_register_resume_10207718(&resume);
    gx8002_xip_watchdog_initialize_10206720(
        3000u, 2999u, gx8002_xip_app_watchdog_callback_10208c98, 0u);
    return 0u;
}
