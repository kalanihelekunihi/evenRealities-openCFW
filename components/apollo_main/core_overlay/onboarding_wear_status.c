/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Protobuf onboarding wear-status notification matched to stock entry
 * 0x0047E320.
 */

typedef __UINTPTR_TYPE__ open_cfw_onboarding_wear_uintptr;

typedef unsigned int (*open_cfw_onboarding_wear_query_function)(void);
typedef unsigned int (*open_cfw_onboarding_wear_mode_query_function)(
    unsigned int
);
typedef int (*open_cfw_onboarding_wear_notify_function)(
    unsigned int,
    const void *
);
typedef unsigned int (*open_cfw_onboarding_wear_log_level_function)(void);
typedef void (*open_cfw_onboarding_wear_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_onboarding_wear_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

struct open_cfw_onboarding_wear_event {
    unsigned int present;
    unsigned int status;
    unsigned int parameter;
};

#ifndef OPEN_CFW_ONBOARDING_WEAR_OTA_ACTIVE
#define OPEN_CFW_ONBOARDING_WEAR_OTA_ACTIVE() \
    (((open_cfw_onboarding_wear_query_function) \
        (open_cfw_onboarding_wear_uintptr)0x004487ADU)())
#endif

#ifndef OPEN_CFW_ONBOARDING_WEAR_TRANSPORT_READY
#define OPEN_CFW_ONBOARDING_WEAR_TRANSPORT_READY() \
    (((open_cfw_onboarding_wear_query_function) \
        (open_cfw_onboarding_wear_uintptr)0x00443485U)())
#endif

#ifndef OPEN_CFW_ONBOARDING_WEAR_MODE_READY
#define OPEN_CFW_ONBOARDING_WEAR_MODE_READY(mode) \
    (((open_cfw_onboarding_wear_mode_query_function) \
        (open_cfw_onboarding_wear_uintptr)0x004434D1U)((mode)))
#endif

#ifndef OPEN_CFW_ONBOARDING_WEAR_NOTIFY
#define OPEN_CFW_ONBOARDING_WEAR_NOTIFY(command, event) \
    (((open_cfw_onboarding_wear_notify_function) \
        (open_cfw_onboarding_wear_uintptr)0x004A8369U)( \
            (command), \
            (event) \
        ))
#endif

#ifndef OPEN_CFW_ONBOARDING_WEAR_LOG_LEVEL
#define OPEN_CFW_ONBOARDING_WEAR_LOG_LEVEL() \
    (((open_cfw_onboarding_wear_log_level_function) \
        (open_cfw_onboarding_wear_uintptr)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_ONBOARDING_WEAR_LOG
#define OPEN_CFW_ONBOARDING_WEAR_LOG(...) \
    (((open_cfw_onboarding_wear_log_function) \
        (open_cfw_onboarding_wear_uintptr)0x0043D575U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_WEAR_TRACE
#define OPEN_CFW_ONBOARDING_WEAR_TRACE(...) \
    (((open_cfw_onboarding_wear_trace_function) \
        (open_cfw_onboarding_wear_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_onboarding_wear_pointer(open_cfw_onboarding_wear_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_onboarding_wear_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_ONBOARDING_WEAR_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_ONBOARDING_WEAR_LOG_LEVEL() & 4U) != 0U;
}

__attribute__((used, noinline))
void open_cfw_onboarding_notify_wear_status_to_app(unsigned int status)
{
    struct open_cfw_onboarding_wear_event event = {
        1U,
        0U,
        0U,
    };
    const void *module =
        open_cfw_onboarding_wear_pointer(0x00781570U);
    const void *file =
        open_cfw_onboarding_wear_pointer(0x006E8ECCU);
    const void *function =
        open_cfw_onboarding_wear_pointer(0x0074BD4CU);
    unsigned int byte_status = (unsigned char)status;
    int result;

    if (OPEN_CFW_ONBOARDING_WEAR_OTA_ACTIVE() == 1U) {
        return;
    }
    if (OPEN_CFW_ONBOARDING_WEAR_TRANSPORT_READY() == 0U) {
        return;
    }
    if (OPEN_CFW_ONBOARDING_WEAR_MODE_READY(0x10U) != 1U) {
        return;
    }

    event.status = byte_status;
    result = OPEN_CFW_ONBOARDING_WEAR_NOTIFY(0U, &event);

    if (result == 0) {
        if ((OPEN_CFW_ONBOARDING_WEAR_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_ONBOARDING_WEAR_LOG(
                4U,
                module,
                file,
                function,
                0x51U,
                open_cfw_onboarding_wear_pointer(0x0072B814U),
                byte_status
            );
        }
        if (open_cfw_onboarding_wear_trace_enabled()) {
            const void *message =
                open_cfw_onboarding_wear_pointer(0x006FBB64U);

            OPEN_CFW_ONBOARDING_WEAR_TRACE(
                0x10400000U,
                message,
                message,
                byte_status
            );
        }
        return;
    }

    if ((OPEN_CFW_ONBOARDING_WEAR_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_ONBOARDING_WEAR_LOG(
            1U,
            module,
            file,
            function,
            0x53U,
            open_cfw_onboarding_wear_pointer(0x00720DA8U),
            result
        );
    }
    if (open_cfw_onboarding_wear_trace_enabled()) {
        const void *message =
            open_cfw_onboarding_wear_pointer(0x006EEC38U);

        OPEN_CFW_ONBOARDING_WEAR_TRACE(
            0x04400000U,
            message,
            message,
            result
        );
    }
}

#undef OPEN_CFW_ONBOARDING_WEAR_TRACE
#undef OPEN_CFW_ONBOARDING_WEAR_LOG
#undef OPEN_CFW_ONBOARDING_WEAR_LOG_LEVEL
#undef OPEN_CFW_ONBOARDING_WEAR_NOTIFY
#undef OPEN_CFW_ONBOARDING_WEAR_MODE_READY
#undef OPEN_CFW_ONBOARDING_WEAR_TRANSPORT_READY
#undef OPEN_CFW_ONBOARDING_WEAR_OTA_ACTIVE
