/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded source replacements for the Apollo510 SPOT-manager public callback
 * dispatch layer at 0x00480312...0x00480433.
 */

typedef __UINTPTR_TYPE__ open_cfw_spotmgr_dispatch_uintptr;

typedef unsigned int (*open_cfw_spotmgr_dispatch_noarg_function)(void);
typedef unsigned int (*open_cfw_spotmgr_dispatch_power_function)(
    unsigned int,
    unsigned int,
    void *
);
typedef unsigned int (*open_cfw_spotmgr_dispatch_ton_function)(
    unsigned int,
    unsigned int
);
typedef void (*open_cfw_spotmgr_dispatch_timer_function)(void);

#define OPEN_CFW_SPOTMGR_DISPATCH_PS_UPDATE_OFFSET 0x04U
#define OPEN_CFW_SPOTMGR_DISPATCH_TEMPCO_POSTPONE_OFFSET 0x0CU
#define OPEN_CFW_SPOTMGR_DISPATCH_TEMPCO_PENDING_OFFSET 0x10U
#define OPEN_CFW_SPOTMGR_DISPATCH_SIMOBUCK_BFR_OVR_OFFSET 0x14U
#define OPEN_CFW_SPOTMGR_DISPATCH_SIMOBUCK_BFR_ENABLE_OFFSET 0x18U
#define OPEN_CFW_SPOTMGR_DISPATCH_SIMOBUCK_AFT_ENABLE_OFFSET 0x1CU
#define OPEN_CFW_SPOTMGR_DISPATCH_TON_INIT_OFFSET 0x20U
#define OPEN_CFW_SPOTMGR_DISPATCH_TON_UPDATE_OFFSET 0x24U
#define OPEN_CFW_SPOTMGR_DISPATCH_POST_LPTOHP_OFFSET 0x28U
#define OPEN_CFW_SPOTMGR_DISPATCH_TIMER_SERVICE_OFFSET 0x2CU
#define OPEN_CFW_SPOTMGR_DISPATCH_AUTOSW_INIT_OFFSET 0x30U
#define OPEN_CFW_SPOTMGR_DISPATCH_AUTOSW_ENABLE_OFFSET 0x34U
#define OPEN_CFW_SPOTMGR_DISPATCH_AUTOSW_DISABLE_OFFSET 0x38U

#ifndef OPEN_CFW_SPOTMGR_DISPATCH_STATE_ADDRESS
#define OPEN_CFW_SPOTMGR_DISPATCH_STATE_ADDRESS 0x20073270U
#endif

#ifndef OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER
#define OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(offset) \
    (*(const volatile unsigned int *)( \
        open_cfw_spotmgr_dispatch_uintptr)( \
            OPEN_CFW_SPOTMGR_DISPATCH_STATE_ADDRESS + (offset)))
#endif

/*
 * The stock wrappers read a callback slot once for the null test and again
 * for the indirect call. Keep both volatile reads: installation can change
 * between them, and callers rely on the public entry points remaining small
 * pass-through dispatchers rather than cached callback owners.
 */
#define OPEN_CFW_SPOTMGR_DISPATCH_NOARG(name, offset) \
    __attribute__((used, noinline)) \
    unsigned int name(void) \
    { \
        open_cfw_spotmgr_dispatch_uintptr handler; \
        handler = (open_cfw_spotmgr_dispatch_uintptr) \
            OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(offset); \
        if (handler == 0U) { \
            return 0U; \
        } \
        handler = (open_cfw_spotmgr_dispatch_uintptr) \
            OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(offset); \
        return ((open_cfw_spotmgr_dispatch_noarg_function)handler)(); \
    }

__attribute__((used, noinline))
unsigned int open_cfw_spotmgr_power_state_update(
    unsigned int stimulus,
    unsigned int enabled,
    void *arguments
)
{
    open_cfw_spotmgr_dispatch_uintptr handler;

    handler = (open_cfw_spotmgr_dispatch_uintptr)
        OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(
            OPEN_CFW_SPOTMGR_DISPATCH_PS_UPDATE_OFFSET
        );
    if (handler == 0U) {
        return 0U;
    }

    handler = (open_cfw_spotmgr_dispatch_uintptr)
        OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(
            OPEN_CFW_SPOTMGR_DISPATCH_PS_UPDATE_OFFSET
        );
    return ((open_cfw_spotmgr_dispatch_power_function)handler)(
        (unsigned int)(unsigned char)stimulus,
        (unsigned int)(unsigned char)enabled,
        arguments
    );
}

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_tempco_postpone,
    OPEN_CFW_SPOTMGR_DISPATCH_TEMPCO_POSTPONE_OFFSET
)

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_tempco_pending_handle,
    OPEN_CFW_SPOTMGR_DISPATCH_TEMPCO_PENDING_OFFSET
)

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_simobuck_init_bfr_ovr,
    OPEN_CFW_SPOTMGR_DISPATCH_SIMOBUCK_BFR_OVR_OFFSET
)

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_simobuck_init_bfr_enable,
    OPEN_CFW_SPOTMGR_DISPATCH_SIMOBUCK_BFR_ENABLE_OFFSET
)

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_simobuck_init_aft_enable,
    OPEN_CFW_SPOTMGR_DISPATCH_SIMOBUCK_AFT_ENABLE_OFFSET
)

__attribute__((used, noinline))
void open_cfw_spotmgr_boost_timer_interrupt_service(void)
{
    open_cfw_spotmgr_dispatch_uintptr handler;

    handler = (open_cfw_spotmgr_dispatch_uintptr)
        OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(
            OPEN_CFW_SPOTMGR_DISPATCH_TIMER_SERVICE_OFFSET
        );
    if (handler != 0U) {
        handler = (open_cfw_spotmgr_dispatch_uintptr)
            OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(
                OPEN_CFW_SPOTMGR_DISPATCH_TIMER_SERVICE_OFFSET
            );
        ((open_cfw_spotmgr_dispatch_timer_function)handler)();
    }
}

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_ton_config_init,
    OPEN_CFW_SPOTMGR_DISPATCH_TON_INIT_OFFSET
)

__attribute__((used, noinline))
unsigned int open_cfw_spotmgr_ton_config_update(
    unsigned int gpu_enabled,
    unsigned int gpu_state
)
{
    open_cfw_spotmgr_dispatch_uintptr handler;

    handler = (open_cfw_spotmgr_dispatch_uintptr)
        OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(
            OPEN_CFW_SPOTMGR_DISPATCH_TON_UPDATE_OFFSET
        );
    if (handler == 0U) {
        return 0U;
    }

    handler = (open_cfw_spotmgr_dispatch_uintptr)
        OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER(
            OPEN_CFW_SPOTMGR_DISPATCH_TON_UPDATE_OFFSET
        );
    return ((open_cfw_spotmgr_dispatch_ton_function)handler)(
        (unsigned int)(unsigned char)gpu_enabled,
        (unsigned int)(unsigned char)gpu_state
    );
}

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_post_lptohp_handle,
    OPEN_CFW_SPOTMGR_DISPATCH_POST_LPTOHP_OFFSET
)

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_simobuck_lp_autosw_init,
    OPEN_CFW_SPOTMGR_DISPATCH_AUTOSW_INIT_OFFSET
)

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_simobuck_lp_autosw_enable,
    OPEN_CFW_SPOTMGR_DISPATCH_AUTOSW_ENABLE_OFFSET
)

OPEN_CFW_SPOTMGR_DISPATCH_NOARG(
    open_cfw_spotmgr_simobuck_lp_autosw_disable,
    OPEN_CFW_SPOTMGR_DISPATCH_AUTOSW_DISABLE_OFFSET
)

#undef OPEN_CFW_SPOTMGR_DISPATCH_NOARG
#undef OPEN_CFW_SPOTMGR_DISPATCH_READ_HANDLER
