/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded lens-status publication and state accessors matched to stock
 * entries 0x0047D818 through 0x0047D8FB.
 */

typedef __UINTPTR_TYPE__ open_cfw_lens_status_uintptr;

typedef unsigned int (*open_cfw_lens_status_query_function)(void);
typedef unsigned int (*open_cfw_lens_status_log_level_function)(void);
typedef void (*open_cfw_lens_status_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_lens_status_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
typedef int (*open_cfw_lens_status_send_function)(
    unsigned int,
    const void *,
    unsigned int,
    unsigned int
);

#ifndef OPEN_CFW_LENS_STATUS_STATE
#define OPEN_CFW_LENS_STATUS_STATE \
    (*(volatile unsigned char *)0x20075043U)
#endif
#ifndef OPEN_CFW_LENS_STATUS_AVAILABLE
#define OPEN_CFW_LENS_STATUS_AVAILABLE() \
    (((open_cfw_lens_status_query_function) \
        (open_cfw_lens_status_uintptr)0x004A2FDDU)())
#endif
#ifndef OPEN_CFW_LENS_STATUS_SELECTOR
#define OPEN_CFW_LENS_STATUS_SELECTOR() \
    (((open_cfw_lens_status_query_function) \
        (open_cfw_lens_status_uintptr)0x004A2915U)())
#endif
#ifndef OPEN_CFW_LENS_STATUS_LOG_LEVEL
#define OPEN_CFW_LENS_STATUS_LOG_LEVEL() \
    (((open_cfw_lens_status_log_level_function) \
        (open_cfw_lens_status_uintptr)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_LENS_STATUS_LOG
#define OPEN_CFW_LENS_STATUS_LOG(...) \
    (((open_cfw_lens_status_log_function) \
        (open_cfw_lens_status_uintptr)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_LENS_STATUS_TRACE
#define OPEN_CFW_LENS_STATUS_TRACE(...) \
    (((open_cfw_lens_status_trace_function) \
        (open_cfw_lens_status_uintptr)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_LENS_STATUS_SEND
#define OPEN_CFW_LENS_STATUS_SEND(command, payload, size, option) \
    (((open_cfw_lens_status_send_function) \
        (open_cfw_lens_status_uintptr)0x00464D1DU)( \
            (command), \
            (payload), \
            (size), \
            (option) \
        ))
#endif

unsigned int open_cfw_status_packet_template6(void);
unsigned int open_cfw_status_packet_template5(void);
unsigned int open_cfw_lens_side(void);

static __attribute__((always_inline)) inline const void *
open_cfw_lens_status_pointer(open_cfw_lens_status_uintptr address)
{
    return (const void *)address;
}

static __attribute__((always_inline)) inline int
open_cfw_lens_status_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_LENS_STATUS_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_LENS_STATUS_LOG_LEVEL() & 4U) != 0U;
}

__attribute__((used, noinline))
void open_cfw_lens_status_publish(void)
{
    if (OPEN_CFW_LENS_STATUS_AVAILABLE() != 0U) {
        if (OPEN_CFW_LENS_STATUS_SELECTOR() != 0U) {
            (void)open_cfw_status_packet_template6();
        } else {
            (void)open_cfw_status_packet_template5();
        }
        return;
    }

    if ((OPEN_CFW_LENS_STATUS_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_LENS_STATUS_LOG(
            4U,
            open_cfw_lens_status_pointer(0x0078C908U),
            open_cfw_lens_status_pointer(0x0070874CU),
            open_cfw_lens_status_pointer(0x00774774U),
            0xFDU,
            open_cfw_lens_status_pointer(0x00730CFCU)
        );
    }
    if (open_cfw_lens_status_trace_enabled()) {
        const void *identity =
            open_cfw_lens_status_pointer(0x00711C64U);

        OPEN_CFW_LENS_STATUS_TRACE(
            0x10000000U,
            identity,
            identity
        );
    }
}

__attribute__((used, noinline))
unsigned int open_cfw_status_packet_template4(unsigned int enabled)
{
    unsigned char payload[8] = {4U, 0U, 1U, 0U, 0U, 0U, 0U, 0U};

    payload[4] = (unsigned char)open_cfw_lens_side();
    payload[5] = open_cfw_lens_side() == 1U ? 2U : 1U;
    payload[6] = enabled != 0U ? 1U : 0U;
    (void)OPEN_CFW_LENS_STATUS_SEND(0x103U, payload, 8U, 0U);
    return 0x00010004U;
}

__attribute__((used, noinline))
unsigned int open_cfw_lens_status_bit0(void)
{
    return OPEN_CFW_LENS_STATUS_STATE & 1U;
}

__attribute__((used, noinline))
unsigned int open_cfw_lens_status_bit1(void)
{
    return (OPEN_CFW_LENS_STATUS_STATE >> 1U) & 1U;
}

__attribute__((used, noinline))
unsigned int open_cfw_lens_status_pair23(void)
{
    return (OPEN_CFW_LENS_STATUS_STATE & 0x0CU) == 0x0CU ? 1U : 0U;
}

__attribute__((used, noinline))
unsigned int open_cfw_lens_status_bit4(void)
{
    return (OPEN_CFW_LENS_STATUS_STATE >> 4U) & 1U;
}

__attribute__((used, noinline))
unsigned int open_cfw_lens_status_bit5(void)
{
    return (OPEN_CFW_LENS_STATUS_STATE >> 5U) & 1U;
}

__attribute__((used, noinline))
unsigned int open_cfw_lens_status_available(void)
{
    return OPEN_CFW_LENS_STATUS_AVAILABLE();
}

__attribute__((used, noinline))
unsigned int open_cfw_lens_status_selected(void)
{
    if (OPEN_CFW_LENS_STATUS_SELECTOR() != 0U) {
        return open_cfw_lens_status_bit4() != 0U ? 1U : 0U;
    }
    return open_cfw_lens_status_bit5() != 0U ? 1U : 0U;
}

#undef OPEN_CFW_LENS_STATUS_SEND
#undef OPEN_CFW_LENS_STATUS_TRACE
#undef OPEN_CFW_LENS_STATUS_LOG
#undef OPEN_CFW_LENS_STATUS_LOG_LEVEL
#undef OPEN_CFW_LENS_STATUS_SELECTOR
#undef OPEN_CFW_LENS_STATUS_AVAILABLE
#undef OPEN_CFW_LENS_STATUS_STATE
