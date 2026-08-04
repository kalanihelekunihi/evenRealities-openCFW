/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Peer onboarding-flag reply matched to stock entry 0x0047E51C.
 */

typedef __UINTPTR_TYPE__ open_cfw_onboarding_peer_reply_uintptr;

typedef void *(*open_cfw_onboarding_peer_reply_zero_function)(
    void *,
    unsigned int,
    unsigned int
);
typedef int (*open_cfw_onboarding_peer_reply_send_function)(
    unsigned int,
    const void *,
    unsigned int,
    unsigned int,
    unsigned int
);
typedef unsigned int (*open_cfw_onboarding_peer_reply_log_level_function)(
    void
);
typedef void (*open_cfw_onboarding_peer_reply_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_onboarding_peer_reply_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_ONBOARDING_PEER_REPLY_ZERO
#define OPEN_CFW_ONBOARDING_PEER_REPLY_ZERO(buffer, size, value) \
    (((open_cfw_onboarding_peer_reply_zero_function) \
        (open_cfw_onboarding_peer_reply_uintptr)0x0043C0E5U)( \
            buffer, \
            size, \
            value \
        ))
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_REPLY_SEND
#define OPEN_CFW_ONBOARDING_PEER_REPLY_SEND(...) \
    (((open_cfw_onboarding_peer_reply_send_function) \
        (open_cfw_onboarding_peer_reply_uintptr)0x00465481U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_REPLY_LOG_LEVEL
#define OPEN_CFW_ONBOARDING_PEER_REPLY_LOG_LEVEL() \
    (((open_cfw_onboarding_peer_reply_log_level_function) \
        (open_cfw_onboarding_peer_reply_uintptr)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_REPLY_LOG
#define OPEN_CFW_ONBOARDING_PEER_REPLY_LOG(...) \
    (((open_cfw_onboarding_peer_reply_log_function) \
        (open_cfw_onboarding_peer_reply_uintptr)0x0043D575U)(__VA_ARGS__))
#endif

#ifndef OPEN_CFW_ONBOARDING_PEER_REPLY_TRACE
#define OPEN_CFW_ONBOARDING_PEER_REPLY_TRACE(...) \
    (((open_cfw_onboarding_peer_reply_trace_function) \
        (open_cfw_onboarding_peer_reply_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_onboarding_peer_reply_pointer(
    open_cfw_onboarding_peer_reply_uintptr address
)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_onboarding_peer_reply_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_ONBOARDING_PEER_REPLY_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_ONBOARDING_PEER_REPLY_LOG_LEVEL() & 4U) != 0U;
}

__attribute__((used, noinline))
void open_cfw_onboarding_flag_reply_to_peer(unsigned int flag)
{
    unsigned char payload[2];
    unsigned int byte_flag = flag & 0xFFU;

    (void)OPEN_CFW_ONBOARDING_PEER_REPLY_ZERO(payload, 2U, 0U);
    payload[0] = 0x0EU;
    payload[1] = (unsigned char)byte_flag;
    (void)OPEN_CFW_ONBOARDING_PEER_REPLY_SEND(
        0x10U,
        payload,
        2U,
        0U,
        5U
    );

    if ((OPEN_CFW_ONBOARDING_PEER_REPLY_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_ONBOARDING_PEER_REPLY_LOG(
            4U,
            open_cfw_onboarding_peer_reply_pointer(0x00781570U),
            open_cfw_onboarding_peer_reply_pointer(0x006E8ECCU),
            open_cfw_onboarding_peer_reply_pointer(0x00762B90U),
            0x8CU,
            open_cfw_onboarding_peer_reply_pointer(0x00779D24U),
            byte_flag
        );
    }
    if (open_cfw_onboarding_peer_reply_trace_enabled()) {
        const void *message =
            open_cfw_onboarding_peer_reply_pointer(0x00740CB4U);

        OPEN_CFW_ONBOARDING_PEER_REPLY_TRACE(
            0x10400000U,
            message,
            message,
            byte_flag
        );
    }
}

#undef OPEN_CFW_ONBOARDING_PEER_REPLY_TRACE
#undef OPEN_CFW_ONBOARDING_PEER_REPLY_LOG
#undef OPEN_CFW_ONBOARDING_PEER_REPLY_LOG_LEVEL
#undef OPEN_CFW_ONBOARDING_PEER_REPLY_SEND
#undef OPEN_CFW_ONBOARDING_PEER_REPLY_ZERO
