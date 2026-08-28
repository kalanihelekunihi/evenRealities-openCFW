/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded BLE connection-parameter event handler matched to stock entry
 * 0x00477ADC.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_event_uintptr;
typedef void (*open_cfw_ble_event_callback)(void *);

typedef unsigned char *(*open_cfw_ble_event_context_function)(void);
typedef unsigned int (*open_cfw_ble_event_state_function)(unsigned char);
typedef unsigned int (*open_cfw_ble_event_tick_function)(void);
typedef unsigned int (*open_cfw_ble_event_log_level_function)(void);
typedef void (*open_cfw_ble_event_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_ble_event_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_BLE_EVENT_CONTEXT
#define OPEN_CFW_BLE_EVENT_CONTEXT() \
    (((open_cfw_ble_event_context_function)0x0046EFCDU)())
#endif
#ifndef OPEN_CFW_BLE_EVENT_CONNECTION_KIND
#define OPEN_CFW_BLE_EVENT_CONNECTION_KIND(identifier) \
    (((open_cfw_ble_event_state_function)0x004B73C5U)(identifier))
#endif
#ifndef OPEN_CFW_BLE_EVENT_TICK
#define OPEN_CFW_BLE_EVENT_TICK() \
    (((open_cfw_ble_event_tick_function)0x004490CDU)())
#endif
#ifndef OPEN_CFW_BLE_EVENT_LOG_LEVEL
#define OPEN_CFW_BLE_EVENT_LOG_LEVEL() \
    (((open_cfw_ble_event_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_BLE_EVENT_LOG
#define OPEN_CFW_BLE_EVENT_LOG(...) \
    (((open_cfw_ble_event_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_EVENT_TRACE
#define OPEN_CFW_BLE_EVENT_TRACE(...) \
    (((open_cfw_ble_event_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_EVENT_CONNECTION_STATE
#define OPEN_CFW_BLE_EVENT_CONNECTION_STATE \
    (*(volatile unsigned short *volatile *)0x2007433CU)
#endif
#ifndef OPEN_CFW_BLE_EVENT_TIMESTAMP
#define OPEN_CFW_BLE_EVENT_TIMESTAMP \
    (*(volatile unsigned int *)0x20074340U)
#endif
#ifndef OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
#define OPEN_CFW_BLE_EVENT_PREVIOUS_MODE \
    (*(volatile unsigned char *)0x20004541U)
#endif
#ifndef OPEN_CFW_BLE_EVENT_CURRENT_MODE
#define OPEN_CFW_BLE_EVENT_CURRENT_MODE \
    (*(volatile unsigned char *)0x20004542U)
#endif
#ifndef OPEN_CFW_BLE_EVENT_REMOTE_ACTIVE
#define OPEN_CFW_BLE_EVENT_REMOTE_ACTIVE \
    (*(volatile unsigned char *)0x20074F8FU)
#endif
#ifndef OPEN_CFW_BLE_EVENT_RETRY_ACTIVE
#define OPEN_CFW_BLE_EVENT_RETRY_ACTIVE \
    (*(volatile unsigned char *)0x20074F90U)
#endif
#ifndef OPEN_CFW_BLE_EVENT_PENDING
#define OPEN_CFW_BLE_EVENT_PENDING \
    (*(volatile unsigned char *)0x20074F91U)
#endif
#ifndef OPEN_CFW_BLE_EVENT_DEFAULTS
#define OPEN_CFW_BLE_EVENT_DEFAULTS \
    ((const volatile unsigned short *)0x00784EA0U)
#endif
#ifndef OPEN_CFW_BLE_EVENT_CALLBACK
#define OPEN_CFW_BLE_EVENT_CALLBACK \
    ((open_cfw_ble_event_callback) \
        (open_cfw_ble_event_uintptr)0x0047761DU)
#endif

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_event_callback callback
);
void open_cfw_event_loop_push_delayed(
    open_cfw_ble_event_callback callback,
    void *argument,
    unsigned int delay
);

static __attribute__((always_inline)) inline const void *
open_cfw_ble_event_pointer(unsigned int address)
{
    return (const void *)(open_cfw_ble_event_uintptr)address;
}

static __attribute__((always_inline)) inline int
open_cfw_ble_event_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_BLE_EVENT_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline unsigned short
open_cfw_ble_event_halfword(
    const unsigned char *event,
    unsigned int offset
)
{
    return *(const unsigned short *)(const void *)(event + offset);
}

static __attribute__((always_inline)) inline const void *
open_cfw_ble_event_mode_name(unsigned char mode)
{
    if (mode == 0xA3U) {
        return open_cfw_ble_event_pointer(0x0078CA04U);
    }
    return open_cfw_ble_event_pointer(0x0078CA0CU);
}

static __attribute__((always_inline)) inline void
open_cfw_ble_event_replace_delay(
    unsigned char mode,
    unsigned int delay
)
{
    (void)open_cfw_event_loop_remove_delayed(OPEN_CFW_BLE_EVENT_CALLBACK);
    open_cfw_event_loop_push_delayed(
        OPEN_CFW_BLE_EVENT_CALLBACK,
        (void *)(open_cfw_ble_event_uintptr)mode,
        delay
    );
}

void open_cfw_ble_connection_handle_event(const unsigned char *event)
{
    const void *module = open_cfw_ble_event_pointer(0x0078A0B8U);
    const void *file = open_cfw_ble_event_pointer(0x006F81BCU);
    const void *function = open_cfw_ble_event_pointer(0x00774FFCU);
    unsigned char identifier = event[0];
    unsigned char status = event[4];
    unsigned short interval = open_cfw_ble_event_halfword(event, 8U);
    unsigned short latency = open_cfw_ble_event_halfword(event, 10U);
    unsigned short timeout = open_cfw_ble_event_halfword(event, 12U);
    unsigned int connection_kind;

    (void)OPEN_CFW_BLE_EVENT_CONTEXT();

    if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_EVENT_LOG(
            4U,
            module,
            file,
            function,
            0x161U,
            open_cfw_ble_event_pointer(0x00726BE8U),
            status,
            OPEN_CFW_BLE_EVENT_CONNECTION_KIND(identifier)
        );
    }
    if (open_cfw_ble_event_trace_enabled()) {
        const void *trace = open_cfw_ble_event_pointer(0x00708F24U);

        OPEN_CFW_BLE_EVENT_TRACE(
            0x10800000U,
            trace,
            trace,
            status,
            OPEN_CFW_BLE_EVENT_CONNECTION_KIND(identifier)
        );
    }

    if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_EVENT_LOG(
            4U,
            module,
            file,
            function,
            0x162U,
            open_cfw_ble_event_pointer(0x00784E90U),
            interval,
            interval,
            latency
        );
    }
    if (open_cfw_ble_event_trace_enabled()) {
        const void *trace = open_cfw_ble_event_pointer(0x0076921CU);

        OPEN_CFW_BLE_EVENT_TRACE(
            0x10C00000U,
            trace,
            trace,
            interval,
            interval,
            latency
        );
    }

    if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_EVENT_LOG(
            4U,
            module,
            file,
            function,
            0x163U,
            open_cfw_ble_event_pointer(0x00774FB4U),
            ((unsigned int)interval * 0x4E2U) / 1000U
        );
    }
    if (open_cfw_ble_event_trace_enabled()) {
        const void *trace = open_cfw_ble_event_pointer(0x0075DCB0U);

        OPEN_CFW_BLE_EVENT_TRACE(
            0x10400000U,
            trace,
            trace,
            ((unsigned int)interval * 0x4E2U) / 1000U
        );
    }

    if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_EVENT_LOG(
            4U,
            module,
            file,
            function,
            0x164U,
            open_cfw_ble_event_pointer(0x0077DD08U),
            latency
        );
    }
    if (open_cfw_ble_event_trace_enabled()) {
        const void *trace = open_cfw_ble_event_pointer(0x007691E4U);

        OPEN_CFW_BLE_EVENT_TRACE(
            0x10400000U,
            trace,
            trace,
            latency
        );
    }

    if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_EVENT_LOG(
            4U,
            module,
            file,
            function,
            0x165U,
            open_cfw_ble_event_pointer(0x0077DD1CU),
            ((unsigned int)timeout * 10000U) / 1000U
        );
    }
    if (open_cfw_ble_event_trace_enabled()) {
        const void *trace = open_cfw_ble_event_pointer(0x0075DC90U);

        OPEN_CFW_BLE_EVENT_TRACE(
            0x10400000U,
            trace,
            trace,
            ((unsigned int)timeout * 10000U) / 1000U
        );
    }

    connection_kind = OPEN_CFW_BLE_EVENT_CONNECTION_KIND(identifier);
    if (connection_kind != 1U) {
        return;
    }

    if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_EVENT_LOG(
            4U,
            module,
            file,
            function,
            0x169U,
            open_cfw_ble_event_pointer(0x00712424U),
            open_cfw_ble_event_mode_name(
                OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
            )
        );
    }
    if (open_cfw_ble_event_trace_enabled()) {
        const void *trace = open_cfw_ble_event_pointer(0x007000A0U);

        OPEN_CFW_BLE_EVENT_TRACE(
            0x10400000U,
            trace,
            trace,
            open_cfw_ble_event_mode_name(
                OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
            )
        );
    }

    if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_EVENT_LOG(
            4U,
            module,
            file,
            function,
            0x16AU,
            open_cfw_ble_event_pointer(0x0075DC70U),
            interval,
            interval,
            latency,
            OPEN_CFW_BLE_EVENT_DEFAULTS[2],
            OPEN_CFW_BLE_EVENT_DEFAULTS[3],
            OPEN_CFW_BLE_EVENT_DEFAULTS[4]
        );
    }
    if (open_cfw_ble_event_trace_enabled()) {
        const void *trace = open_cfw_ble_event_pointer(0x0073BF88U);

        OPEN_CFW_BLE_EVENT_TRACE(
            0x11800000U,
            trace,
            trace,
            interval,
            interval,
            latency,
            OPEN_CFW_BLE_EVENT_DEFAULTS[2],
            OPEN_CFW_BLE_EVENT_DEFAULTS[3],
            OPEN_CFW_BLE_EVENT_DEFAULTS[4]
        );
    }

    if (status != 0U) {
        if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_EVENT_LOG(
                2U,
                module,
                file,
                function,
                0x172U,
                open_cfw_ble_event_pointer(0x00708F64U),
                status
            );
        }
        if (open_cfw_ble_event_trace_enabled()) {
            const void *trace = open_cfw_ble_event_pointer(0x006F1684U);

            OPEN_CFW_BLE_EVENT_TRACE(
                0x08400000U,
                trace,
                trace,
                status
            );
        }
        if (status == 12U || status == 59U) {
            if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
                OPEN_CFW_BLE_EVENT_LOG(
                    2U,
                    module,
                    file,
                    function,
                    0x177U,
                    open_cfw_ble_event_pointer(0x006E6184U),
                    status
                );
            }
            if (open_cfw_ble_event_trace_enabled()) {
                const void *trace =
                    open_cfw_ble_event_pointer(0x006DC3F4U);

                OPEN_CFW_BLE_EVENT_TRACE(
                    0x08400000U,
                    trace,
                    trace,
                    status
                );
            }
            OPEN_CFW_BLE_EVENT_TIMESTAMP = OPEN_CFW_BLE_EVENT_TICK();
            OPEN_CFW_BLE_EVENT_RETRY_ACTIVE = 1U;
            OPEN_CFW_BLE_EVENT_PENDING = 0U;
            open_cfw_ble_event_replace_delay(
                OPEN_CFW_BLE_EVENT_PREVIOUS_MODE,
                30000U
            );
            return;
        }
    }

    {
        unsigned char desired_mode;
        unsigned int threshold =
            OPEN_CFW_BLE_EVENT_REMOTE_ACTIVE != 0U ? 72U : 25U;

        desired_mode = interval < threshold ? 0xA3U : 0xA4U;
        if (desired_mode == OPEN_CFW_BLE_EVENT_PREVIOUS_MODE) {
            volatile unsigned short *state =
                OPEN_CFW_BLE_EVENT_CONNECTION_STATE;

            state[12] = interval;
            state[13] = latency;
            state[14] = timeout;
            OPEN_CFW_BLE_EVENT_CURRENT_MODE =
                OPEN_CFW_BLE_EVENT_PREVIOUS_MODE;
            ((volatile unsigned char *)(void *)state)[0x1EU] =
                OPEN_CFW_BLE_EVENT_PREVIOUS_MODE == 0xA3U ? 1U : 0U;

            if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
                OPEN_CFW_BLE_EVENT_LOG(
                    3U,
                    module,
                    file,
                    function,
                    0x1A5U,
                    open_cfw_ble_event_pointer(0x00751CF8U),
                    open_cfw_ble_event_mode_name(
                        OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
                    )
                );
            }
            if (open_cfw_ble_event_trace_enabled()) {
                const void *trace =
                    open_cfw_ble_event_pointer(0x00731694U);

                OPEN_CFW_BLE_EVENT_TRACE(
                    0x0C400000U,
                    trace,
                    trace,
                    open_cfw_ble_event_mode_name(
                        OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
                    )
                );
            }
            OPEN_CFW_BLE_EVENT_RETRY_ACTIVE = 0U;
            OPEN_CFW_BLE_EVENT_PENDING = 0U;
        }
        else {
            if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
                OPEN_CFW_BLE_EVENT_LOG(
                    1U,
                    module,
                    file,
                    function,
                    0x18DU,
                    open_cfw_ble_event_pointer(0x007475E4U),
                    open_cfw_ble_event_mode_name(
                        OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
                    )
                );
            }
            if (open_cfw_ble_event_trace_enabled()) {
                const void *trace =
                    open_cfw_ble_event_pointer(0x00726C1CU);

                OPEN_CFW_BLE_EVENT_TRACE(
                    0x04400000U,
                    trace,
                    trace,
                    open_cfw_ble_event_mode_name(
                        OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
                    )
                );
            }

            if (status != 0U) {
                if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
                    OPEN_CFW_BLE_EVENT_LOG(
                        2U,
                        module,
                        file,
                        function,
                        0x191U,
                        open_cfw_ble_event_pointer(0x00712460U)
                    );
                }
                if (open_cfw_ble_event_trace_enabled()) {
                    const void *trace =
                        open_cfw_ble_event_pointer(0x007000E4U);

                    OPEN_CFW_BLE_EVENT_TRACE(
                        0x08000000U,
                        trace,
                        trace
                    );
                }
                OPEN_CFW_BLE_EVENT_TIMESTAMP = OPEN_CFW_BLE_EVENT_TICK();
                OPEN_CFW_BLE_EVENT_RETRY_ACTIVE = 1U;
                OPEN_CFW_BLE_EVENT_PENDING = 0U;
                open_cfw_ble_event_replace_delay(
                    OPEN_CFW_BLE_EVENT_PREVIOUS_MODE,
                    10000U
                );
            }
            else {
                unsigned int delay =
                    OPEN_CFW_BLE_EVENT_PREVIOUS_MODE == 0xA3U
                    ? 2000U
                    : 4000U;

                OPEN_CFW_BLE_EVENT_RETRY_ACTIVE = 0U;
                OPEN_CFW_BLE_EVENT_PENDING = 0U;
                open_cfw_ble_event_replace_delay(
                    OPEN_CFW_BLE_EVENT_PREVIOUS_MODE,
                    delay
                );
            }
        }
    }

    if (OPEN_CFW_BLE_EVENT_REMOTE_ACTIVE != 0U) {
        if ((OPEN_CFW_BLE_EVENT_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_EVENT_LOG(
                4U,
                module,
                file,
                function,
                0x1ADU,
                open_cfw_ble_event_pointer(0x0071BE40U),
                OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
            );
        }
        if (open_cfw_ble_event_trace_enabled()) {
            const void *trace = open_cfw_ble_event_pointer(0x00700128U);

            OPEN_CFW_BLE_EVENT_TRACE(
                0x10400000U,
                trace,
                trace,
                OPEN_CFW_BLE_EVENT_PREVIOUS_MODE
            );
        }

        if (OPEN_CFW_BLE_EVENT_PREVIOUS_MODE == 0xA4U) {
            OPEN_CFW_BLE_EVENT_REMOTE_ACTIVE = 0U;
        }
        else {
            open_cfw_ble_event_replace_delay(0xA4U, 60000U);
        }
    }
}
