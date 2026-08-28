/*
 * SPDX-License-Identifier: MIT
 *
 * Peer onboarding-flag notification matched to stock entry 0x0047E4A6.
 */

typedef __UINTPTR_TYPE__ open_cfw_onboarding_peer_flag_uintptr;

typedef unsigned int (*open_cfw_onboarding_peer_flag_get_function)(void);
typedef void *(*open_cfw_onboarding_peer_flag_zero_function)(
    void *,
    unsigned int,
    unsigned int
);
typedef int (*open_cfw_onboarding_peer_flag_send_function)(
    unsigned int,
    const void *,
    unsigned int,
    unsigned int,
    unsigned int
);
typedef unsigned int (*open_cfw_onboarding_peer_flag_log_level_function)(
    void
);
typedef void (*open_cfw_onboarding_peer_flag_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_onboarding_peer_flag_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_ONBOARDING_PEER_FLAG_GET
#define OPEN_CFW_ONBOARDING_PEER_FLAG_GET() \
    (((open_cfw_onboarding_peer_flag_get_function) \
        (open_cfw_onboarding_peer_flag_uintptr)0x004A7833U)())
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_FLAG_ZERO
#define OPEN_CFW_ONBOARDING_PEER_FLAG_ZERO(buffer, size, value) \
    (((open_cfw_onboarding_peer_flag_zero_function) \
        (open_cfw_onboarding_peer_flag_uintptr)0x0043C0E5U)( \
            buffer, \
            size, \
            value \
        ))
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_FLAG_SEND
#define OPEN_CFW_ONBOARDING_PEER_FLAG_SEND(...) \
    (((open_cfw_onboarding_peer_flag_send_function) \
        (open_cfw_onboarding_peer_flag_uintptr)0x00465481U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_FLAG_LOG_LEVEL
#define OPEN_CFW_ONBOARDING_PEER_FLAG_LOG_LEVEL() \
    (((open_cfw_onboarding_peer_flag_log_level_function) \
        (open_cfw_onboarding_peer_flag_uintptr)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_FLAG_LOG
#define OPEN_CFW_ONBOARDING_PEER_FLAG_LOG(...) \
    (((open_cfw_onboarding_peer_flag_log_function) \
        (open_cfw_onboarding_peer_flag_uintptr)0x0043D575U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_FLAG_TRACE
#define OPEN_CFW_ONBOARDING_PEER_FLAG_TRACE(...) \
    (((open_cfw_onboarding_peer_flag_trace_function) \
        (open_cfw_onboarding_peer_flag_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_onboarding_peer_flag_pointer(
    open_cfw_onboarding_peer_flag_uintptr address
)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_onboarding_peer_flag_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_ONBOARDING_PEER_FLAG_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_ONBOARDING_PEER_FLAG_LOG_LEVEL() & 4U) != 0U;
}

__attribute__((used, noinline))
void open_cfw_onboarding_flag_send_to_peer(void)
{
    unsigned int flag = OPEN_CFW_ONBOARDING_PEER_FLAG_GET();
    unsigned char payload[2];
    unsigned int byte_flag = flag & 0xFFU;

    (void)OPEN_CFW_ONBOARDING_PEER_FLAG_ZERO(payload, 2U, 0U);
    payload[0] = 0x0DU;
    payload[1] = (unsigned char)byte_flag;
    (void)OPEN_CFW_ONBOARDING_PEER_FLAG_SEND(
        0x10U,
        payload,
        2U,
        0U,
        5U
    );

    if ((OPEN_CFW_ONBOARDING_PEER_FLAG_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_ONBOARDING_PEER_FLAG_LOG(
            4U,
            open_cfw_onboarding_peer_flag_pointer(0x00781570U),
            open_cfw_onboarding_peer_flag_pointer(0x006E8ECCU),
            open_cfw_onboarding_peer_flag_pointer(0x00762B70U),
            0x7FU,
            open_cfw_onboarding_peer_flag_pointer(0x00779D0CU),
            byte_flag
        );
    }
    if (open_cfw_onboarding_peer_flag_trace_enabled()) {
        const void *message =
            open_cfw_onboarding_peer_flag_pointer(0x00740C88U);

        OPEN_CFW_ONBOARDING_PEER_FLAG_TRACE(
            0x10400000U,
            message,
            message,
            byte_flag
        );
    }
}

#undef OPEN_CFW_ONBOARDING_PEER_FLAG_TRACE
#undef OPEN_CFW_ONBOARDING_PEER_FLAG_LOG
#undef OPEN_CFW_ONBOARDING_PEER_FLAG_LOG_LEVEL
#undef OPEN_CFW_ONBOARDING_PEER_FLAG_SEND
#undef OPEN_CFW_ONBOARDING_PEER_FLAG_ZERO
#undef OPEN_CFW_ONBOARDING_PEER_FLAG_GET
