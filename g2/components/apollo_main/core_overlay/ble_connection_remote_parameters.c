/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE remote connection-parameter handler matched to stock entry
 * 0x00477774.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_remote_uintptr;
typedef void (*open_cfw_ble_remote_callback)(void *);

typedef unsigned int (*open_cfw_ble_remote_role_function)(void);
typedef unsigned int (*open_cfw_ble_remote_log_level_function)(void);
typedef void (*open_cfw_ble_remote_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_ble_remote_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_BLE_REMOTE_CONNECTION_STATE
#define OPEN_CFW_BLE_REMOTE_CONNECTION_STATE \
    (*(volatile unsigned short *volatile *)0x2007433CU)
#endif
#ifndef OPEN_CFW_BLE_REMOTE_PREVIOUS_MODE
#define OPEN_CFW_BLE_REMOTE_PREVIOUS_MODE \
    (*(volatile unsigned char *)0x20004541U)
#endif
#ifndef OPEN_CFW_BLE_REMOTE_CURRENT_MODE
#define OPEN_CFW_BLE_REMOTE_CURRENT_MODE \
    (*(volatile unsigned char *)0x20004542U)
#endif
#ifndef OPEN_CFW_BLE_REMOTE_ACTIVE
#define OPEN_CFW_BLE_REMOTE_ACTIVE \
    (*(volatile unsigned char *)0x20074F8FU)
#endif
#ifndef OPEN_CFW_BLE_REMOTE_ROLE
#define OPEN_CFW_BLE_REMOTE_ROLE() \
    (((open_cfw_ble_remote_role_function)0x0046C631U)())
#endif
#ifndef OPEN_CFW_BLE_REMOTE_LOG_LEVEL
#define OPEN_CFW_BLE_REMOTE_LOG_LEVEL() \
    (((open_cfw_ble_remote_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_BLE_REMOTE_LOG
#define OPEN_CFW_BLE_REMOTE_LOG(...) \
    (((open_cfw_ble_remote_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_REMOTE_TRACE
#define OPEN_CFW_BLE_REMOTE_TRACE(...) \
    (((open_cfw_ble_remote_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_REMOTE_CALLBACK
#define OPEN_CFW_BLE_REMOTE_CALLBACK \
    ((open_cfw_ble_remote_callback) \
        (open_cfw_ble_remote_uintptr)0x0047761DU)
#endif

unsigned int open_cfw_ble_connection_select_secondary(
    const volatile unsigned short *state
);
unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_remote_callback callback
);
void open_cfw_event_loop_push_delayed(
    open_cfw_ble_remote_callback callback,
    void *argument,
    unsigned int delay
);

static __attribute__((always_inline)) inline const void *
open_cfw_ble_remote_pointer(unsigned int address)
{
    return (const void *)(open_cfw_ble_remote_uintptr)address;
}

static __attribute__((always_inline)) inline int
open_cfw_ble_remote_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_BLE_REMOTE_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline unsigned short
open_cfw_ble_remote_halfword(
    const unsigned char *parameters,
    unsigned int offset
)
{
    return *(const unsigned short *)(const void *)(parameters + offset);
}

void open_cfw_ble_connection_apply_remote_parameters(
    const unsigned char *parameters
)
{
    volatile unsigned short *state =
        OPEN_CFW_BLE_REMOTE_CONNECTION_STATE;
    const void *module = open_cfw_ble_remote_pointer(0x0078A0B8U);
    const void *file = open_cfw_ble_remote_pointer(0x006F81BCU);
    const void *function = open_cfw_ble_remote_pointer(0x00774FCCU);
    unsigned short interval = open_cfw_ble_remote_halfword(parameters, 16U);
    unsigned short latency = open_cfw_ble_remote_halfword(parameters, 18U);
    unsigned short timeout = open_cfw_ble_remote_halfword(parameters, 20U);
    unsigned char mode;
    const void *mode_name;

    if ((OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_REMOTE_LOG(
            4U,
            module,
            file,
            function,
            0x141U,
            open_cfw_ble_remote_pointer(0x0077DD58U)
        );
    }
    if (open_cfw_ble_remote_trace_enabled()) {
        const void *trace = open_cfw_ble_remote_pointer(0x0075DCD0U);

        OPEN_CFW_BLE_REMOTE_TRACE(0x10000000U, trace, trace);
    }

    if ((OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_REMOTE_LOG(
            4U,
            module,
            file,
            function,
            0x142U,
            open_cfw_ble_remote_pointer(0x00784E80U),
            open_cfw_ble_remote_halfword(parameters, 6U)
        );
    }
    if (open_cfw_ble_remote_trace_enabled()) {
        const void *trace = open_cfw_ble_remote_pointer(0x00769200U);

        OPEN_CFW_BLE_REMOTE_TRACE(
            0x10400000U,
            trace,
            trace,
            open_cfw_ble_remote_halfword(parameters, 6U)
        );
    }

    if ((OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_REMOTE_LOG(
            4U,
            module,
            file,
            function,
            0x143U,
            open_cfw_ble_remote_pointer(0x0078A0C4U),
            parameters[8]
        );
    }
    if (open_cfw_ble_remote_trace_enabled()) {
        const void *trace = open_cfw_ble_remote_pointer(0x00774FE4U);

        OPEN_CFW_BLE_REMOTE_TRACE(
            0x10400000U,
            trace,
            trace,
            parameters[8]
        );
    }

    if ((OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_REMOTE_LOG(
            4U,
            module,
            file,
            function,
            0x144U,
            open_cfw_ble_remote_pointer(0x00747594U),
            parameters[15],
            parameters[14],
            parameters[13],
            parameters[12],
            parameters[11],
            parameters[10]
        );
    }
    if (open_cfw_ble_remote_trace_enabled()) {
        const void *trace = open_cfw_ble_remote_pointer(0x00731664U);

        OPEN_CFW_BLE_REMOTE_TRACE(
            0x11800000U,
            trace,
            trace,
            parameters[15],
            parameters[14],
            parameters[13],
            parameters[12],
            parameters[11],
            parameters[10]
        );
    }

    if ((OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_REMOTE_LOG(
            4U,
            module,
            file,
            function,
            0x145U,
            open_cfw_ble_remote_pointer(0x00774FB4U),
            ((unsigned int)interval * 0x4E2U) / 1000U
        );
    }
    if (open_cfw_ble_remote_trace_enabled()) {
        const void *trace = open_cfw_ble_remote_pointer(0x0075DCB0U);

        OPEN_CFW_BLE_REMOTE_TRACE(
            0x10400000U,
            trace,
            trace,
            ((unsigned int)interval * 0x4E2U) / 1000U
        );
    }

    if ((OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_REMOTE_LOG(
            4U,
            module,
            file,
            function,
            0x146U,
            open_cfw_ble_remote_pointer(0x0077DD08U),
            latency
        );
    }
    if (open_cfw_ble_remote_trace_enabled()) {
        const void *trace = open_cfw_ble_remote_pointer(0x007691E4U);

        OPEN_CFW_BLE_REMOTE_TRACE(
            0x10400000U,
            trace,
            trace,
            latency
        );
    }

    if ((OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_REMOTE_LOG(
            4U,
            module,
            file,
            function,
            0x147U,
            open_cfw_ble_remote_pointer(0x0077DD1CU),
            ((unsigned int)timeout * 10000U) / 1000U
        );
    }
    if (open_cfw_ble_remote_trace_enabled()) {
        const void *trace = open_cfw_ble_remote_pointer(0x0075DC90U);

        OPEN_CFW_BLE_REMOTE_TRACE(
            0x10400000U,
            trace,
            trace,
            ((unsigned int)timeout * 10000U) / 1000U
        );
    }

    state[12] = interval;
    state[13] = latency;
    state[14] = timeout;
    mode = (unsigned char)open_cfw_ble_connection_select_secondary(state);
    OPEN_CFW_BLE_REMOTE_CURRENT_MODE = mode;
    OPEN_CFW_BLE_REMOTE_PREVIOUS_MODE = mode;
    OPEN_CFW_BLE_REMOTE_ACTIVE = 1U;

    mode_name = open_cfw_ble_remote_pointer(0x0078CA0CU);
    if (mode == 0xA3U) {
        mode_name = open_cfw_ble_remote_pointer(0x0078CA04U);
    }
    if ((OPEN_CFW_BLE_REMOTE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_REMOTE_LOG(
            4U,
            module,
            file,
            function,
            0x14EU,
            open_cfw_ble_remote_pointer(0x007475BCU),
            interval,
            mode_name
        );
    }
    if (open_cfw_ble_remote_trace_enabled()) {
        const void *trace = open_cfw_ble_remote_pointer(0x00726BB4U);

        OPEN_CFW_BLE_REMOTE_TRACE(
            0x10800000U,
            trace,
            trace,
            interval,
            mode_name
        );
    }

    (void)open_cfw_event_loop_remove_delayed(
        OPEN_CFW_BLE_REMOTE_CALLBACK
    );
    if (OPEN_CFW_BLE_REMOTE_ROLE() == 0U) {
        open_cfw_event_loop_push_delayed(
            OPEN_CFW_BLE_REMOTE_CALLBACK,
            (void *)(open_cfw_ble_remote_uintptr)0xA4U,
            60000U
        );
    }
}
