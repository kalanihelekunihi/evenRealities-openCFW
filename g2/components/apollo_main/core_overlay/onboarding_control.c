/*
 * SPDX-License-Identifier: MIT
 *
 * Protobuf onboarding control-state update matched to stock entry
 * 0x0047E2D0.
 */

typedef __UINTPTR_TYPE__ open_cfw_onboarding_control_uintptr;

typedef unsigned int (*open_cfw_onboarding_mutex_acquire_function)(
    void *,
    unsigned int
);
typedef unsigned int (*open_cfw_onboarding_mutex_release_function)(void *);

#ifndef OPEN_CFW_ONBOARDING_CONTROL_STATE
#define OPEN_CFW_ONBOARDING_CONTROL_STATE \
    ((volatile unsigned char *) \
        (open_cfw_onboarding_control_uintptr)0x200F4800U)
#endif

#ifndef OPEN_CFW_ONBOARDING_CONTROL_MUTEX
#define OPEN_CFW_ONBOARDING_CONTROL_MUTEX \
    (*(void * volatile *) \
        (open_cfw_onboarding_control_uintptr)0x20074830U)
#endif

#ifndef OPEN_CFW_ONBOARDING_CONTROL_MUTEX_ACQUIRE
#define OPEN_CFW_ONBOARDING_CONTROL_MUTEX_ACQUIRE(mutex, wait_ticks) \
    (((open_cfw_onboarding_mutex_acquire_function) \
        (open_cfw_onboarding_control_uintptr)0x004497B7U)( \
            (mutex), \
            (wait_ticks) \
        ))
#endif

#ifndef OPEN_CFW_ONBOARDING_CONTROL_MUTEX_RELEASE
#define OPEN_CFW_ONBOARDING_CONTROL_MUTEX_RELEASE(mutex) \
    (((open_cfw_onboarding_mutex_release_function) \
        (open_cfw_onboarding_control_uintptr)0x0044981DU)((mutex)))
#endif

#define OPEN_CFW_ONBOARDING_CONTROL_CONFIG 1U
#define OPEN_CFW_ONBOARDING_CONTROL_EVENT 2U
#define OPEN_CFW_ONBOARDING_CONTROL_EVENT_WITH_PARAMETER 3U
#define OPEN_CFW_ONBOARDING_CONTROL_WAIT_FOREVER 0xFFFFFFFFU
#define OPEN_CFW_ONBOARDING_CONTROL_CONFIG_READY 2U

__attribute__((used, noinline))
int open_cfw_onboarding_control_update(
    unsigned int command,
    const unsigned char *payload
)
{
    volatile unsigned char *state = OPEN_CFW_ONBOARDING_CONTROL_STATE;

    state[2] = 0U;
    command = (unsigned char)command;

    if (command == OPEN_CFW_ONBOARDING_CONTROL_CONFIG) {
        (void)OPEN_CFW_ONBOARDING_CONTROL_MUTEX_ACQUIRE(
            OPEN_CFW_ONBOARDING_CONTROL_MUTEX,
            OPEN_CFW_ONBOARDING_CONTROL_WAIT_FOREVER
        );
        if (state[0] != payload[0]) {
            state[1] = 0U;
        }
        state[0] = payload[0];
        state[2] = OPEN_CFW_ONBOARDING_CONTROL_CONFIG_READY;
        (void)OPEN_CFW_ONBOARDING_CONTROL_MUTEX_RELEASE(
            OPEN_CFW_ONBOARDING_CONTROL_MUTEX
        );
        return 0;
    }

    if (
        command == OPEN_CFW_ONBOARDING_CONTROL_EVENT
        || command == OPEN_CFW_ONBOARDING_CONTROL_EVENT_WITH_PARAMETER
    ) {
        return 0;
    }
    return 1;
}

#undef OPEN_CFW_ONBOARDING_CONTROL_CONFIG_READY
#undef OPEN_CFW_ONBOARDING_CONTROL_WAIT_FOREVER
#undef OPEN_CFW_ONBOARDING_CONTROL_EVENT_WITH_PARAMETER
#undef OPEN_CFW_ONBOARDING_CONTROL_EVENT
#undef OPEN_CFW_ONBOARDING_CONTROL_CONFIG
#undef OPEN_CFW_ONBOARDING_CONTROL_MUTEX_RELEASE
#undef OPEN_CFW_ONBOARDING_CONTROL_MUTEX_ACQUIRE
#undef OPEN_CFW_ONBOARDING_CONTROL_MUTEX
#undef OPEN_CFW_ONBOARDING_CONTROL_STATE
