/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded BLE connection-parameter mode coordinator matched to stock entry
 * 0x0047720C.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_coordinator_uintptr;
typedef void (*open_cfw_ble_coordinator_callback)(void *);

typedef unsigned char *(*open_cfw_ble_coordinator_context_function)(void);
typedef void *(*open_cfw_ble_coordinator_allocate_function)(unsigned int);
typedef void (*open_cfw_ble_coordinator_send_function)(
    unsigned char,
    void *
);
typedef unsigned int (*open_cfw_ble_coordinator_log_level_function)(void);
typedef void (*open_cfw_ble_coordinator_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_ble_coordinator_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_BLE_COORDINATOR_CONTEXT
#define OPEN_CFW_BLE_COORDINATOR_CONTEXT() \
    (((open_cfw_ble_coordinator_context_function)0x0046EFCDU)())
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_PENDING
#define OPEN_CFW_BLE_COORDINATOR_PENDING \
    (*(volatile unsigned char *)0x20074F91U)
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_PREVIOUS_MODE
#define OPEN_CFW_BLE_COORDINATOR_PREVIOUS_MODE \
    (*(volatile unsigned char *)0x20004541U)
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE
#define OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE \
    (*(volatile unsigned char *)0x20004542U)
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE
#define OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE \
    (*(const volatile unsigned short *volatile *)0x2007433CU)
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_ENDPOINT
#define OPEN_CFW_BLE_COORDINATOR_ENDPOINT \
    (*(volatile unsigned char *)0x20074F8EU)
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_ALLOCATE
#define OPEN_CFW_BLE_COORDINATOR_ALLOCATE(size) \
    (((open_cfw_ble_coordinator_allocate_function)0x004BF99FU)(size))
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_SEND
#define OPEN_CFW_BLE_COORDINATOR_SEND(endpoint, packet) \
    (((open_cfw_ble_coordinator_send_function)0x004BF9BBU)( \
        (endpoint), (packet) \
    ))
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL
#define OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() \
    (((open_cfw_ble_coordinator_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_LOG
#define OPEN_CFW_BLE_COORDINATOR_LOG(...) \
    (((open_cfw_ble_coordinator_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_TRACE
#define OPEN_CFW_BLE_COORDINATOR_TRACE(...) \
    (((open_cfw_ble_coordinator_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_COORDINATOR_CALLBACK
#define OPEN_CFW_BLE_COORDINATOR_CALLBACK \
    ((open_cfw_ble_coordinator_callback) \
        (open_cfw_ble_coordinator_uintptr)0x0047761DU)
#endif

unsigned int open_cfw_ble_connection_select_primary(
    const volatile unsigned short *state
);
unsigned int open_cfw_ble_connection_select_secondary(
    const volatile unsigned short *state
);
unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_coordinator_callback callback
);
void open_cfw_event_loop_push_delayed(
    open_cfw_ble_coordinator_callback callback,
    void *argument,
    unsigned int delay
);

static __attribute__((always_inline)) inline const void *
open_cfw_ble_coordinator_pointer(unsigned int address)
{
    return (const void *)(open_cfw_ble_coordinator_uintptr)address;
}

static __attribute__((always_inline)) inline int
open_cfw_ble_coordinator_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 4U) != 0U;
}

void open_cfw_ble_connection_coordinate(
    unsigned int mode_argument,
    unsigned int unused_2,
    unsigned int unused_3,
    unsigned int diagnostic_argument
)
{
    unsigned char *context = OPEN_CFW_BLE_COORDINATOR_CONTEXT();
    unsigned char mode = (unsigned char)mode_argument;
    const void *module =
        open_cfw_ble_coordinator_pointer(0x0078A0B8U);
    const void *file =
        open_cfw_ble_coordinator_pointer(0x006F81BCU);
    const void *function =
        open_cfw_ble_coordinator_pointer(0x00774F9CU);

    (void)unused_2;
    (void)unused_3;
    if (
        context == (unsigned char *)0
        || context[4] == 0U
        || context[4] > 3U
    ) {
        if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_COORDINATOR_LOG(
                2U,
                module,
                file,
                function,
                0xEDU,
                open_cfw_ble_coordinator_pointer(0x0071BE08U),
                context
            );
        }
        if (open_cfw_ble_coordinator_trace_enabled()) {
            const void *trace =
                open_cfw_ble_coordinator_pointer(0x0070005CU);

            OPEN_CFW_BLE_COORDINATOR_TRACE(
                0x08400000U,
                trace,
                trace,
                context
            );
        }
        OPEN_CFW_BLE_COORDINATOR_PENDING = 0U;
        return;
    }

    if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_COORDINATOR_LOG(
            4U,
            module,
            file,
            function,
            0xF2U,
            open_cfw_ble_coordinator_pointer(0x0073BFB4U),
            mode,
            OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE,
            OPEN_CFW_BLE_COORDINATOR_PREVIOUS_MODE,
            diagnostic_argument
        );
    }
    if (open_cfw_ble_coordinator_trace_enabled()) {
        const void *trace =
            open_cfw_ble_coordinator_pointer(0x00726B4CU);

        OPEN_CFW_BLE_COORDINATOR_TRACE(
            0x10C00000U,
            trace,
            trace,
            mode,
            OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE,
            OPEN_CFW_BLE_COORDINATOR_PREVIOUS_MODE
        );
    }

    if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_COORDINATOR_LOG(
            4U,
            module,
            file,
            function,
            0xF3U,
            open_cfw_ble_coordinator_pointer(0x00774FB4U),
            (
                (unsigned int)OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE[12]
                * 0x4E2U
            ) / 1000U
        );
    }
    if (open_cfw_ble_coordinator_trace_enabled()) {
        const void *trace =
            open_cfw_ble_coordinator_pointer(0x0075DCB0U);

        OPEN_CFW_BLE_COORDINATOR_TRACE(
            0x10400000U,
            trace,
            trace,
            (
                (unsigned int)OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE[12]
                * 0x4E2U
            ) / 1000U
        );
    }

    if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_COORDINATOR_LOG(
            4U,
            module,
            file,
            function,
            0xF4U,
            open_cfw_ble_coordinator_pointer(0x0077DD08U),
            OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE[13]
        );
    }
    if (open_cfw_ble_coordinator_trace_enabled()) {
        const void *trace =
            open_cfw_ble_coordinator_pointer(0x007691E4U);

        OPEN_CFW_BLE_COORDINATOR_TRACE(
            0x10400000U,
            trace,
            trace,
            OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE[13]
        );
    }

    if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_COORDINATOR_LOG(
            4U,
            module,
            file,
            function,
            0xF5U,
            open_cfw_ble_coordinator_pointer(0x0077DD1CU),
            (
                (unsigned int)OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE[14]
                * 10000U
            ) / 1000U
        );
    }
    if (open_cfw_ble_coordinator_trace_enabled()) {
        const void *trace =
            open_cfw_ble_coordinator_pointer(0x0075DC90U);

        OPEN_CFW_BLE_COORDINATOR_TRACE(
            0x10400000U,
            trace,
            trace,
            (
                (unsigned int)OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE[14]
                * 10000U
            ) / 1000U
        );
    }

    if (mode == 0xA4U) {
        unsigned char selected = (unsigned char)
            open_cfw_ble_connection_select_secondary(
                OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE
            );

        if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_COORDINATOR_LOG(
                4U,
                module,
                file,
                function,
                0xF8U,
                open_cfw_ble_coordinator_pointer(0x00712370U),
                mode,
                OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE,
                selected
            );
        }
        if (open_cfw_ble_coordinator_trace_enabled()) {
            const void *trace =
                open_cfw_ble_coordinator_pointer(0x006F8204U);

            OPEN_CFW_BLE_COORDINATOR_TRACE(
                0x10C00000U,
                trace,
                trace,
                mode,
                OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE,
                selected
            );
        }
        if (selected == 0xA4U) {
            OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE = selected;
            return;
        }
    }
    else if (mode == 0xA3U) {
        unsigned char selected = (unsigned char)
            open_cfw_ble_connection_select_primary(
                OPEN_CFW_BLE_COORDINATOR_CONNECTION_STATE
            );

        if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_COORDINATOR_LOG(
                4U,
                module,
                file,
                function,
                0xFFU,
                open_cfw_ble_coordinator_pointer(0x007123ACU),
                mode,
                OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE,
                selected
            );
        }
        if (open_cfw_ble_coordinator_trace_enabled()) {
            const void *trace =
                open_cfw_ble_coordinator_pointer(0x006F824CU);

            OPEN_CFW_BLE_COORDINATOR_TRACE(
                0x10C00000U,
                trace,
                trace,
                mode,
                OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE,
                selected
            );
        }
        if (selected == 0xA3U) {
            OPEN_CFW_BLE_COORDINATOR_CURRENT_MODE = selected;
            OPEN_CFW_BLE_COORDINATOR_PENDING = 0U;
            return;
        }
    }

    if (
        OPEN_CFW_BLE_COORDINATOR_PENDING != 0U
        && mode == OPEN_CFW_BLE_COORDINATOR_PREVIOUS_MODE
    ) {
        if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_COORDINATOR_LOG(
                4U,
                module,
                file,
                function,
                0x109U,
                open_cfw_ble_coordinator_pointer(0x006F1638U),
                mode
            );
        }
        if (open_cfw_ble_coordinator_trace_enabled()) {
            const void *trace =
                open_cfw_ble_coordinator_pointer(0x006E6130U);

            OPEN_CFW_BLE_COORDINATOR_TRACE(
                0x10400000U,
                trace,
                trace,
                mode
            );
        }
        OPEN_CFW_BLE_COORDINATOR_PENDING = 0U;
        (void)open_cfw_event_loop_remove_delayed(
            OPEN_CFW_BLE_COORDINATOR_CALLBACK
        );
        open_cfw_event_loop_push_delayed(
            OPEN_CFW_BLE_COORDINATOR_CALLBACK,
            (void *)(open_cfw_ble_coordinator_uintptr)mode,
            10000U
        );
        return;
    }

    if ((OPEN_CFW_BLE_COORDINATOR_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_COORDINATOR_LOG(
            4U,
            module,
            file,
            function,
            0x110U,
            open_cfw_ble_coordinator_pointer(0x00751CB0U),
            mode
        );
    }
    if (open_cfw_ble_coordinator_trace_enabled()) {
        const void *trace =
            open_cfw_ble_coordinator_pointer(0x007315D4U);

        OPEN_CFW_BLE_COORDINATOR_TRACE(
            0x10400000U,
            trace,
            trace,
            mode
        );
    }
    OPEN_CFW_BLE_COORDINATOR_PENDING = 1U;
    {
        unsigned char *packet =
            (unsigned char *)OPEN_CFW_BLE_COORDINATOR_ALLOCATE(12U);

        if (packet != (unsigned char *)0) {
            packet[2] = mode;
            *(unsigned short *)(void *)packet = context[4];
            OPEN_CFW_BLE_COORDINATOR_SEND(
                OPEN_CFW_BLE_COORDINATOR_ENDPOINT,
                packet
            );
        }
    }
}
