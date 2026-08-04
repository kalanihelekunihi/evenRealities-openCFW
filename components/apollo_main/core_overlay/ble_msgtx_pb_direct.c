/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE transmit wrappers matched to stock entries from
 * 0x00475A38 through 0x00475ED3.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_msgtx_pb_direct_uintptr;

#ifndef OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE
typedef unsigned int (*open_cfw_ble_msgtx_pb_direct_ota_active_function)(
    void
);
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE() \
    (((open_cfw_ble_msgtx_pb_direct_ota_active_function)0x004487ADU)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_PB_SEND_SIDE_REJECTED
typedef unsigned int (
    *open_cfw_ble_msgtx_pb_send_side_rejected_function
)(void);
#define OPEN_CFW_BLE_MSGTX_PB_SEND_SIDE_REJECTED() \
    (((open_cfw_ble_msgtx_pb_send_side_rejected_function)0x0046F259U)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_PB_NOTIFY_COMMAND_ROLE
typedef unsigned int (
    *open_cfw_ble_msgtx_pb_notify_command_role_function
)(void);
#define OPEN_CFW_BLE_MSGTX_PB_NOTIFY_COMMAND_ROLE() \
    (((open_cfw_ble_msgtx_pb_notify_command_role_function)0x0046F1D1U)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE
int open_cfw_ble_msgtx_enqueue(
    unsigned char transport,
    unsigned char enabled,
    unsigned char argument_1,
    unsigned char argument_2,
    const void *payload,
    unsigned short length
);
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE( \
    transport, enabled, argument_1, argument_2, payload, length \
) \
    open_cfw_ble_msgtx_enqueue( \
        (transport), \
        (enabled), \
        (argument_1), \
        (argument_2), \
        (payload), \
        (length) \
    )
#endif

#ifndef OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG_LEVEL
typedef unsigned int (*open_cfw_ble_msgtx_pb_direct_log_level_function)(
    void
);
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG_LEVEL() \
    (((open_cfw_ble_msgtx_pb_direct_log_level_function)0x0043D0CFU)())
#endif

#ifndef OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG
typedef void (*open_cfw_ble_msgtx_pb_direct_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *
);
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG( \
    level, module, file, function, line, message \
) \
    (((open_cfw_ble_msgtx_pb_direct_log_function)0x0043D575U)( \
        (level), \
        (module), \
        (file), \
        (function), \
        (line), \
        (message) \
    ))
#endif

#ifndef OPEN_CFW_BLE_MSGTX_PB_DIRECT_TRACE
typedef void (*open_cfw_ble_msgtx_pb_direct_trace_function)(
    unsigned int,
    const void *,
    const void *
);
#define OPEN_CFW_BLE_MSGTX_PB_DIRECT_TRACE(level, format, argument) \
    (((open_cfw_ble_msgtx_pb_direct_trace_function)0x0043CE9FU)( \
        (level), \
        (format), \
        (argument) \
    ))
#endif

static __attribute__((always_inline)) inline int
open_cfw_ble_msgtx_pb_diagnostic(
    unsigned int line,
    const void *function,
    const void *structured_message,
    const void *trace_message
)
{
    unsigned int level;

    level = OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG_LEVEL();
    if ((level & 2U) != 0U) {
        OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG(
            4U,
            (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x0078C644U,
            (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x006FE2C4U,
            function,
            line,
            structured_message
        );
    }

    level = OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG_LEVEL();
    if (
        (level & 1U) != 0U
        || (
            OPEN_CFW_BLE_MSGTX_PB_DIRECT_LOG_LEVEL() & 4U
        ) != 0U
    ) {
        OPEN_CFW_BLE_MSGTX_PB_DIRECT_TRACE(
            0x10000000U,
            trace_message,
            trace_message
        );
    }

    return 0;
}

static __attribute__((always_inline)) inline int
open_cfw_ble_msgtx_pb_send_common(
    unsigned int argument_1,
    unsigned int argument_2,
    const void *payload,
    unsigned int length,
    unsigned char enabled,
    unsigned int line,
    const void *function,
    const void *structured_message,
    const void *trace_message
)
{
    if (OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE() == 0U) {
        return OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE(
            0U,
            enabled,
            (unsigned char)argument_1,
            (unsigned char)argument_2,
            payload,
            (unsigned short)length
        );
    }

    return open_cfw_ble_msgtx_pb_diagnostic(
        line,
        function,
        structured_message,
        trace_message
    );
}

int open_cfw_ble_msgtx_pb_direct_send(
    unsigned int argument_1,
    unsigned int argument_2,
    const void *payload,
    unsigned int length
)
{
    return open_cfw_ble_msgtx_pb_send_common(
        argument_1,
        argument_2,
        payload,
        length,
        0U,
        0x198U,
        (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x00773584U,
        (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x0075BA54U,
        (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x00739CA4U
    );
}

int open_cfw_ble_msgtx_pb_notify_direct_send(
    unsigned int argument_1,
    unsigned int argument_2,
    const void *payload,
    unsigned int length
)
{
    return open_cfw_ble_msgtx_pb_send_common(
        argument_1,
        argument_2,
        payload,
        length,
        1U,
        0x1A2U,
        (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x007668F0U,
        (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x0074FC1CU,
        (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x0072F08CU
    );
}

int open_cfw_ble_msgtx_pb_send(
    unsigned int argument_1,
    unsigned int argument_2,
    const void *payload,
    unsigned int length
)
{
    const void *function =
        (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x0078420CU;

    if (OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE() != 0U) {
        return open_cfw_ble_msgtx_pb_diagnostic(
            0x1ACU,
            function,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x007735A0U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x0074FC44U
        );
    }

    if (OPEN_CFW_BLE_MSGTX_PB_SEND_SIDE_REJECTED() != 0U) {
        open_cfw_ble_msgtx_pb_diagnostic(
            0x1B9U,
            function,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x00766930U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x007453B0U
        );
        return 8;
    }

    return OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE(
        0U,
        0U,
        (unsigned char)argument_1,
        (unsigned char)argument_2,
        payload,
        (unsigned short)length
    );
}

int open_cfw_ble_msgtx_pb_notify(
    unsigned int argument_1,
    unsigned int argument_2,
    const void *payload,
    unsigned int length
)
{
    const void *function =
        (const void *)(open_cfw_ble_msgtx_pb_direct_uintptr)0x0077CBBCU;

    if (OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE() != 0U) {
        return open_cfw_ble_msgtx_pb_diagnostic(
            0x1C4U,
            function,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x00766950U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x007453DCU
        );
    }

    if (OPEN_CFW_BLE_MSGTX_PB_SEND_SIDE_REJECTED() != 0U) {
        open_cfw_ble_msgtx_pb_diagnostic(
            0x1D0U,
            function,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x0075BA78U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x00745408U
        );
        return 8;
    }

    if (OPEN_CFW_BLE_MSGTX_PB_NOTIFY_COMMAND_ROLE() == 0U) {
        open_cfw_ble_msgtx_pb_diagnostic(
            0x1D5U,
            function,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x007735BCU,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x0074FC6CU
        );
        return 8;
    }

    return OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE(
        0U,
        1U,
        (unsigned char)argument_1,
        (unsigned char)argument_2,
        payload,
        (unsigned short)length
    );
}

int open_cfw_ble_msgtx_stream_notify(
    const void *payload,
    unsigned int length
)
{
    if (OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE() != 0U) {
        return open_cfw_ble_msgtx_pb_diagnostic(
            0x1E9U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x00766970U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x0074FC94U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x0072F0C0U
        );
    }

    return OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE(
        1U,
        1U,
        0U,
        0U,
        payload,
        (unsigned short)length
    );
}

int open_cfw_ble_msgtx_transport3_send(
    unsigned int argument_1,
    unsigned int argument_2,
    const void *payload,
    unsigned int length
)
{
    return OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE(
        3U,
        0U,
        (unsigned char)argument_1,
        (unsigned char)argument_2,
        payload,
        (unsigned short)length
    );
}

int open_cfw_ble_msgtx_efs_send(
    unsigned int argument_1,
    unsigned int argument_2,
    const void *payload,
    unsigned int length
)
{
    if (OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE() != 0U) {
        return open_cfw_ble_msgtx_pb_diagnostic(
            0x1FDU,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x0077CBD4U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x007735D8U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x0074FCBCU
        );
    }

    return OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE(
        2U,
        0U,
        (unsigned char)argument_1,
        (unsigned char)argument_2,
        payload,
        (unsigned short)length
    );
}

int open_cfw_ble_msgtx_efs_notify(
    unsigned int argument_1,
    unsigned int argument_2,
    const void *payload,
    unsigned int length
)
{
    if (OPEN_CFW_BLE_MSGTX_PB_DIRECT_OTA_ACTIVE() != 0U) {
        open_cfw_ble_msgtx_pb_diagnostic(
            0x207U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x007735F4U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x00766990U,
            (const void *)
                (open_cfw_ble_msgtx_pb_direct_uintptr)0x00745434U
        );
        return 8;
    }

    return OPEN_CFW_BLE_MSGTX_PB_DIRECT_ENQUEUE(
        2U,
        1U,
        (unsigned char)argument_1,
        (unsigned char)argument_2,
        payload,
        (unsigned short)length
    );
}
