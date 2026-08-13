/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE connection-parameter update/scheduling reimplementation
 * matched to stock entry 0x00476CBC.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_connection_uintptr;
typedef void (*open_cfw_ble_connection_callback)(void *);

typedef unsigned int (*open_cfw_ble_connection_status_function)(
    unsigned char
);
typedef void (*open_cfw_ble_connection_update_function)(
    unsigned char,
    const unsigned short *
);
typedef unsigned int (*open_cfw_ble_connection_log_level_function)(void);
typedef void (*open_cfw_ble_connection_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_ble_connection_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_BLE_CONNECTION_DEFAULTS
#define OPEN_CFW_BLE_CONNECTION_DEFAULTS \
    (*(const volatile unsigned short *volatile *)0x2007435CU)
#endif
#ifndef OPEN_CFW_BLE_CONNECTION_STATUS
#define OPEN_CFW_BLE_CONNECTION_STATUS(index) \
    (((open_cfw_ble_connection_status_function)0x004B73A3U)(index))
#endif
#ifndef OPEN_CFW_BLE_CONNECTION_UPDATE
#define OPEN_CFW_BLE_CONNECTION_UPDATE(index, parameters) \
    (((open_cfw_ble_connection_update_function)0x004B6D27U)( \
        (index), (parameters) \
    ))
#endif
#ifndef OPEN_CFW_BLE_CONNECTION_LOG_LEVEL
#define OPEN_CFW_BLE_CONNECTION_LOG_LEVEL() \
    (((open_cfw_ble_connection_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_BLE_CONNECTION_LOG
#define OPEN_CFW_BLE_CONNECTION_LOG(...) \
    (((open_cfw_ble_connection_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_CONNECTION_TRACE
#define OPEN_CFW_BLE_CONNECTION_TRACE(...) \
    (((open_cfw_ble_connection_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif

unsigned char open_cfw_event_loop_remove_delayed(
    open_cfw_ble_connection_callback callback
);
void open_cfw_event_loop_push_delayed(
    open_cfw_ble_connection_callback callback,
    void *argument,
    unsigned int delay
);

static __attribute__((always_inline)) inline int
open_cfw_ble_connection_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_BLE_CONNECTION_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_BLE_CONNECTION_LOG_LEVEL() & 4U) != 0U;
}

void open_cfw_ble_connection_schedule(
    unsigned char mode,
    unsigned char *state
)
{
    unsigned int status = OPEN_CFW_BLE_CONNECTION_STATUS(state[4]);
    unsigned int ready = status == 0U;

    if ((OPEN_CFW_BLE_CONNECTION_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_CONNECTION_LOG(
            4U,
            (const void *)
                (open_cfw_ble_connection_uintptr)0x0078A0B8U,
            (const void *)
                (open_cfw_ble_connection_uintptr)0x006F81BCU,
            (const void *)
                (open_cfw_ble_connection_uintptr)0x0077DCE0U,
            0xA0U,
            (const void *)
                (open_cfw_ble_connection_uintptr)0x0075DC50U,
            ready,
            state[10],
            OPEN_CFW_BLE_CONNECTION_STATUS(state[4]) & 0xFFFFU
        );
    }
    if (open_cfw_ble_connection_trace_enabled()) {
        const void *trace =
            (const void *)
                (open_cfw_ble_connection_uintptr)0x0074756CU;

        OPEN_CFW_BLE_CONNECTION_TRACE(
            0x10C00000U,
            trace,
            trace,
            ready,
            state[10],
            OPEN_CFW_BLE_CONNECTION_STATUS(state[4]) & 0xFFFFU
        );
    }

    if (ready != 0U && state[10] != 0U) {
        const volatile unsigned short *defaults =
            OPEN_CFW_BLE_CONNECTION_DEFAULTS;
        unsigned short parameters[6];

        ++state[12];
        parameters[0] = defaults[2];
        parameters[1] = defaults[3];
        parameters[2] = defaults[4];
        parameters[3] = defaults[5];
        parameters[4] = 0U;
        parameters[5] = 0xFFFFU;
        OPEN_CFW_BLE_CONNECTION_UPDATE(state[4], parameters);
        return;
    }

    state[10] = (unsigned char)ready;
    {
        open_cfw_ble_connection_callback callback =
            (open_cfw_ble_connection_callback)
                (open_cfw_ble_connection_uintptr)0x0047761DU;
        unsigned int delay = mode == 0xA3U ? 2000U : 4000U;

        (void)open_cfw_event_loop_remove_delayed(callback);
        open_cfw_event_loop_push_delayed(
            callback,
            (void *)(open_cfw_ble_connection_uintptr)mode,
            delay
        );
    }
}
