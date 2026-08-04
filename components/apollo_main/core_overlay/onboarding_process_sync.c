/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Peer onboarding-process synchronization matched to stock entry 0x0047E58E.
 */

typedef __UINTPTR_TYPE__ open_cfw_onboarding_process_sync_uintptr;

typedef void *(*open_cfw_onboarding_process_sync_zero_function)(
    void *,
    unsigned int,
    unsigned int
);
typedef int (*open_cfw_onboarding_process_sync_send_function)(
    unsigned int,
    const void *,
    unsigned int,
    unsigned int,
    unsigned int
);
typedef unsigned int (*open_cfw_onboarding_process_sync_log_level_function)(
    void
);
typedef void (*open_cfw_onboarding_process_sync_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_onboarding_process_sync_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_ONBOARDING_PROCESS_SYNC_ZERO
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_ZERO(buffer, size, value) \
    (((open_cfw_onboarding_process_sync_zero_function) \
        (open_cfw_onboarding_process_sync_uintptr)0x0043C0E5U)( \
            buffer, \
            size, \
            value \
        ))
#endif

#ifndef OPEN_CFW_ONBOARDING_PROCESS_SYNC_SEND
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_SEND(...) \
    (((open_cfw_onboarding_process_sync_send_function) \
        (open_cfw_onboarding_process_sync_uintptr)0x00465481U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG_LEVEL
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG_LEVEL() \
    (((open_cfw_onboarding_process_sync_log_level_function) \
        (open_cfw_onboarding_process_sync_uintptr)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG(...) \
    (((open_cfw_onboarding_process_sync_log_function) \
        (open_cfw_onboarding_process_sync_uintptr)0x0043D575U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_PROCESS_SYNC_TRACE
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_TRACE(...) \
    (((open_cfw_onboarding_process_sync_trace_function) \
        (open_cfw_onboarding_process_sync_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_PROCESS_SYNC_STATE
#define OPEN_CFW_ONBOARDING_PROCESS_SYNC_STATE() \
    ((volatile const unsigned char *) \
        (open_cfw_onboarding_process_sync_uintptr)0x200F4800U)
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_onboarding_process_sync_pointer(
    open_cfw_onboarding_process_sync_uintptr address
)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_onboarding_process_sync_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG_LEVEL() & 4U) != 0U;
}

__attribute__((used, noinline))
void open_cfw_onboarding_process_sync_to_peer(void)
{
    volatile const unsigned char *state =
        OPEN_CFW_ONBOARDING_PROCESS_SYNC_STATE();
    unsigned char payload[3];

    (void)OPEN_CFW_ONBOARDING_PROCESS_SYNC_ZERO(payload, 3U, 0U);
    payload[0] = 0x09U;
    payload[1] = state[0];
    payload[2] = state[1];
    (void)OPEN_CFW_ONBOARDING_PROCESS_SYNC_SEND(
        0x10U,
        payload,
        3U,
        0U,
        5U
    );

    if ((OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG(
            4U,
            open_cfw_onboarding_process_sync_pointer(0x00781570U),
            open_cfw_onboarding_process_sync_pointer(0x006E8ECCU),
            open_cfw_onboarding_process_sync_pointer(0x00762BB0U),
            0x9AU,
            open_cfw_onboarding_process_sync_pointer(0x0074BD74U),
            (unsigned int)state[0],
            (unsigned int)state[1]
        );
    }
    if (open_cfw_onboarding_process_sync_trace_enabled()) {
        const void *message =
            open_cfw_onboarding_process_sync_pointer(0x00716F9CU);

        OPEN_CFW_ONBOARDING_PROCESS_SYNC_TRACE(
            0x10800000U,
            message,
            message,
            (unsigned int)state[0],
            (unsigned int)state[1]
        );
    }
}

#undef OPEN_CFW_ONBOARDING_PROCESS_SYNC_STATE
#undef OPEN_CFW_ONBOARDING_PROCESS_SYNC_TRACE
#undef OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG
#undef OPEN_CFW_ONBOARDING_PROCESS_SYNC_LOG_LEVEL
#undef OPEN_CFW_ONBOARDING_PROCESS_SYNC_SEND
#undef OPEN_CFW_ONBOARDING_PROCESS_SYNC_ZERO
