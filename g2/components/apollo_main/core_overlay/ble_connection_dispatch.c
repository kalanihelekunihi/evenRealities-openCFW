/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE connection-event dispatcher matched to stock entry
 * 0x004782DC.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_dispatch_uintptr;
typedef void (*open_cfw_ble_dispatch_callback)(void *);

typedef unsigned int (*open_cfw_ble_dispatch_profile_function)(void);
typedef unsigned int (*open_cfw_ble_dispatch_kind_function)(unsigned char);
typedef unsigned int (*open_cfw_ble_dispatch_log_level_function)(void);
typedef void (*open_cfw_ble_dispatch_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_ble_dispatch_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);
typedef void (*open_cfw_ble_dispatch_coordinate_function)(unsigned char);

#ifndef OPEN_CFW_BLE_DISPATCH_STATE_BASE
#define OPEN_CFW_BLE_DISPATCH_STATE_BASE \
    ((unsigned char *)0x200717B0U)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_PENDING
#define OPEN_CFW_BLE_DISPATCH_PENDING \
    (*(volatile unsigned char *)0x20074F91U)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_PREVIOUS_MODE
#define OPEN_CFW_BLE_DISPATCH_PREVIOUS_MODE \
    (*(volatile unsigned char *)0x20004541U)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_DEFAULTS
#define OPEN_CFW_BLE_DISPATCH_DEFAULTS \
    (*(const volatile unsigned short *volatile *)0x2007435CU)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_SHORT_PRIMARY
#define OPEN_CFW_BLE_DISPATCH_SHORT_PRIMARY \
    ((const volatile unsigned short *) \
        (open_cfw_ble_dispatch_uintptr)0x00784EC0U)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_SHORT_SECONDARY
#define OPEN_CFW_BLE_DISPATCH_SHORT_SECONDARY \
    ((const volatile unsigned short *) \
        (open_cfw_ble_dispatch_uintptr)0x00784EB0U)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_LONG_DEFAULTS
#define OPEN_CFW_BLE_DISPATCH_LONG_DEFAULTS \
    ((const volatile unsigned short *) \
        (open_cfw_ble_dispatch_uintptr)0x00784EA0U)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_PROFILE
#define OPEN_CFW_BLE_DISPATCH_PROFILE() \
    (((open_cfw_ble_dispatch_profile_function)0x004B8129U)())
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_KIND
#define OPEN_CFW_BLE_DISPATCH_KIND(identifier) \
    (((open_cfw_ble_dispatch_kind_function)0x004B73C5U)(identifier))
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_LOG_LEVEL
#define OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() \
    (((open_cfw_ble_dispatch_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_LOG
#define OPEN_CFW_BLE_DISPATCH_LOG(...) \
    (((open_cfw_ble_dispatch_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_TRACE
#define OPEN_CFW_BLE_DISPATCH_TRACE(...) \
    (((open_cfw_ble_dispatch_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_CALLBACK
#define OPEN_CFW_BLE_DISPATCH_CALLBACK \
    ((open_cfw_ble_dispatch_callback) \
        (open_cfw_ble_dispatch_uintptr)0x0047761DU)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_COORDINATE
#define OPEN_CFW_BLE_DISPATCH_COORDINATE(mode) \
    (((open_cfw_ble_dispatch_coordinate_function)0x0047720DU)(mode))
#endif

void open_cfw_ble_connection_apply_remote_parameters(
    const unsigned char *parameters
);
void open_cfw_ble_connection_handle_event(const unsigned char *event);
void open_cfw_ble_connection_schedule(
    unsigned char mode,
    unsigned char *state
);
unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_dispatch_callback callback
);

#ifndef OPEN_CFW_BLE_DISPATCH_APPLY_REMOTE
#define OPEN_CFW_BLE_DISPATCH_APPLY_REMOTE(parameters) \
    open_cfw_ble_connection_apply_remote_parameters(parameters)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_HANDLE_EVENT
#define OPEN_CFW_BLE_DISPATCH_HANDLE_EVENT(event) \
    open_cfw_ble_connection_handle_event(event)
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_SCHEDULE
#define OPEN_CFW_BLE_DISPATCH_SCHEDULE(mode, state) \
    open_cfw_ble_connection_schedule((mode), (state))
#endif
#ifndef OPEN_CFW_BLE_DISPATCH_REMOVE
#define OPEN_CFW_BLE_DISPATCH_REMOVE(callback) \
    open_cfw_event_loop_remove_delayed(callback)
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_ble_dispatch_pointer(unsigned int address)
{
    return (const void *)(open_cfw_ble_dispatch_uintptr)address;
}

static __attribute__((always_inline)) inline unsigned short
open_cfw_ble_dispatch_halfword(
    const unsigned char *message,
    unsigned int offset
)
{
    return *(const unsigned short *)(const void *)(message + offset);
}

static __attribute__((always_inline)) inline int
open_cfw_ble_dispatch_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_BLE_DISPATCH_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline unsigned char *
open_cfw_ble_dispatch_state(unsigned short identifier)
{
    if (identifier == 0U || identifier >= 4U) {
        return (unsigned char *)0;
    }
    return OPEN_CFW_BLE_DISPATCH_STATE_BASE
        + ((unsigned int)identifier - 1U) * 0x30U;
}

static __attribute__((always_inline)) inline void
open_cfw_ble_dispatch_invalid_state(
    unsigned short identifier,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int trace_identity
)
{
    if ((OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_DISPATCH_LOG(
            1U,
            open_cfw_ble_dispatch_pointer(0x0078A0B8U),
            open_cfw_ble_dispatch_pointer(0x006F81BCU),
            open_cfw_ble_dispatch_pointer(0x00775014U),
            line,
            open_cfw_ble_dispatch_pointer(structured_identity),
            identifier
        );
    }
    if (open_cfw_ble_dispatch_trace_enabled()) {
        const void *identity =
            open_cfw_ble_dispatch_pointer(trace_identity);

        OPEN_CFW_BLE_DISPATCH_TRACE(
            0x04400000U,
            identity,
            identity,
            identifier
        );
    }
    OPEN_CFW_BLE_DISPATCH_PENDING = 0U;
}

static __attribute__((always_inline)) inline void
open_cfw_ble_dispatch_state_diagnostic(
    unsigned char *state,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int trace_identity
)
{
    if ((OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_DISPATCH_LOG(
            4U,
            open_cfw_ble_dispatch_pointer(0x0078A0B8U),
            open_cfw_ble_dispatch_pointer(0x006F81BCU),
            open_cfw_ble_dispatch_pointer(0x00775014U),
            line,
            open_cfw_ble_dispatch_pointer(structured_identity),
            state
        );
    }
    if (open_cfw_ble_dispatch_trace_enabled()) {
        const void *identity =
            open_cfw_ble_dispatch_pointer(trace_identity);

        OPEN_CFW_BLE_DISPATCH_TRACE(
            0x10400000U,
            identity,
            identity,
            state
        );
    }
}

static __attribute__((always_inline)) inline void
open_cfw_ble_dispatch_defaults_diagnostic(
    const volatile unsigned short *defaults,
    unsigned int line,
    unsigned int structured_identity,
    unsigned int trace_identity
)
{
    if ((OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_DISPATCH_LOG(
            4U,
            open_cfw_ble_dispatch_pointer(0x0078A0B8U),
            open_cfw_ble_dispatch_pointer(0x006F81BCU),
            open_cfw_ble_dispatch_pointer(0x00775014U),
            line,
            open_cfw_ble_dispatch_pointer(structured_identity),
            defaults[2],
            defaults[3]
        );
    }
    if (open_cfw_ble_dispatch_trace_enabled()) {
        const void *identity =
            open_cfw_ble_dispatch_pointer(trace_identity);

        OPEN_CFW_BLE_DISPATCH_TRACE(
            0x10800000U,
            identity,
            identity,
            defaults[2],
            defaults[3]
        );
    }
}

void open_cfw_ble_connection_dispatch(
    unsigned int unused_endpoint,
    const unsigned char *message
)
{
    unsigned short identifier;
    unsigned char *state;

    (void)unused_endpoint;
    if (message == (const unsigned char *)0) {
        return;
    }

    identifier = open_cfw_ble_dispatch_halfword(message, 0U);
    state = open_cfw_ble_dispatch_state(identifier);

    switch (message[2]) {
    case 0x27U:
        if (OPEN_CFW_BLE_DISPATCH_KIND((unsigned char)identifier) == 1U) {
            OPEN_CFW_BLE_DISPATCH_APPLY_REMOTE(message);
        }
        return;

    case 0x28U:
        (void)OPEN_CFW_BLE_DISPATCH_REMOVE(
            OPEN_CFW_BLE_DISPATCH_CALLBACK
        );
        OPEN_CFW_BLE_DISPATCH_PENDING = 0U;
        return;

    case 0x29U:
        OPEN_CFW_BLE_DISPATCH_HANDLE_EVENT(message);
        return;

    case 0x40U:
        if ((OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_DISPATCH_LOG(
                4U,
                open_cfw_ble_dispatch_pointer(0x0078A0B8U),
                open_cfw_ble_dispatch_pointer(0x006F81BCU),
                open_cfw_ble_dispatch_pointer(0x00775014U),
                0x23EU,
                open_cfw_ble_dispatch_pointer(0x0074760CU)
            );
        }
        if (open_cfw_ble_dispatch_trace_enabled()) {
            const void *identity =
                open_cfw_ble_dispatch_pointer(0x00726C84U);

            OPEN_CFW_BLE_DISPATCH_TRACE(
                0x10000000U,
                identity,
                identity
            );
        }
        if ((OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_DISPATCH_LOG(
                4U,
                open_cfw_ble_dispatch_pointer(0x0078A0B8U),
                open_cfw_ble_dispatch_pointer(0x006F81BCU),
                open_cfw_ble_dispatch_pointer(0x00775014U),
                0x243U,
                open_cfw_ble_dispatch_pointer(0x0071BEB0U),
                open_cfw_ble_dispatch_halfword(message, 6U),
                open_cfw_ble_dispatch_halfword(message, 8U),
                open_cfw_ble_dispatch_halfword(message, 10U),
                open_cfw_ble_dispatch_halfword(message, 12U)
            );
        }
        if (open_cfw_ble_dispatch_trace_enabled()) {
            const void *identity =
                open_cfw_ble_dispatch_pointer(0x0070016CU);

            OPEN_CFW_BLE_DISPATCH_TRACE(
                0x11000000U,
                identity,
                identity,
                open_cfw_ble_dispatch_halfword(message, 6U),
                open_cfw_ble_dispatch_halfword(message, 8U),
                open_cfw_ble_dispatch_halfword(message, 10U),
                open_cfw_ble_dispatch_halfword(message, 12U)
            );
        }
        return;

    case 0xA3U:
        if (state == (unsigned char *)0) {
            open_cfw_ble_dispatch_invalid_state(
                identifier,
                0x20EU,
                0x007316C4U,
                0x0071249CU
            );
            return;
        }
        open_cfw_ble_dispatch_state_diagnostic(
            state,
            0x212U,
            0x00751D1CU,
            0x007316F4U
        );
        if (OPEN_CFW_BLE_DISPATCH_PROFILE() == 4U) {
            OPEN_CFW_BLE_DISPATCH_DEFAULTS =
                OPEN_CFW_BLE_DISPATCH_SHORT_PRIMARY;
            open_cfw_ble_dispatch_defaults_diagnostic(
                OPEN_CFW_BLE_DISPATCH_DEFAULTS,
                0x215U,
                0x00726C50U,
                0x00708FA4U
            );
        }
        else {
            OPEN_CFW_BLE_DISPATCH_DEFAULTS =
                OPEN_CFW_BLE_DISPATCH_SHORT_SECONDARY;
            open_cfw_ble_dispatch_defaults_diagnostic(
                OPEN_CFW_BLE_DISPATCH_DEFAULTS,
                0x219U,
                0x00731724U,
                0x007124D8U
            );
        }
        OPEN_CFW_BLE_DISPATCH_SCHEDULE(0xA3U, state);
        OPEN_CFW_BLE_DISPATCH_PREVIOUS_MODE = 0xA3U;
        return;

    case 0xA4U:
        if (state == (unsigned char *)0) {
            open_cfw_ble_dispatch_invalid_state(
                identifier,
                0x222U,
                0x00731754U,
                0x00712514U
            );
            return;
        }
        open_cfw_ble_dispatch_state_diagnostic(
            state,
            0x226U,
            0x00751D40U,
            0x00731784U
        );
        OPEN_CFW_BLE_DISPATCH_DEFAULTS =
            OPEN_CFW_BLE_DISPATCH_LONG_DEFAULTS;
        open_cfw_ble_dispatch_defaults_diagnostic(
            OPEN_CFW_BLE_DISPATCH_DEFAULTS,
            0x228U,
            0x0073C00CU,
            0x0071BE78U
        );
        OPEN_CFW_BLE_DISPATCH_SCHEDULE(0xA4U, state);
        OPEN_CFW_BLE_DISPATCH_PREVIOUS_MODE = 0xA4U;
        return;

    case 0xB9U:
        {
            unsigned char mode =
                (unsigned char)open_cfw_ble_dispatch_halfword(message, 8U);

            if ((OPEN_CFW_BLE_DISPATCH_LOG_LEVEL() & 2U) != 0U) {
                OPEN_CFW_BLE_DISPATCH_LOG(
                    4U,
                    open_cfw_ble_dispatch_pointer(0x0078A0B8U),
                    open_cfw_ble_dispatch_pointer(0x006F81BCU),
                    open_cfw_ble_dispatch_pointer(0x00775014U),
                    0x249U,
                    open_cfw_ble_dispatch_pointer(0x00751D64U),
                    mode
                );
            }
            if (open_cfw_ble_dispatch_trace_enabled()) {
                const void *identity =
                    open_cfw_ble_dispatch_pointer(0x007317B4U);

                OPEN_CFW_BLE_DISPATCH_TRACE(
                    0x10400000U,
                    identity,
                    identity,
                    mode
                );
            }
            OPEN_CFW_BLE_DISPATCH_COORDINATE(mode);
        }
        return;

    default:
        return;
    }
}
