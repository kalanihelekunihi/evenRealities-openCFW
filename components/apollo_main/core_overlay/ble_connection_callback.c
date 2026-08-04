/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE connection-parameter delayed callback matched to stock entry
 * 0x0047761C.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_callback_uintptr;

typedef unsigned char *(*open_cfw_ble_callback_state_function)(void);
typedef unsigned int (*open_cfw_ble_callback_role_function)(void);
typedef void *(*open_cfw_ble_callback_allocate_function)(unsigned int);
typedef void (*open_cfw_ble_callback_send_function)(
    unsigned char,
    void *
);
typedef unsigned int (*open_cfw_ble_callback_log_level_function)(void);
typedef void (*open_cfw_ble_callback_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_ble_callback_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_BLE_CALLBACK_CONTROLLER
#define OPEN_CFW_BLE_CALLBACK_CONTROLLER() \
    (((open_cfw_ble_callback_state_function)0x004B8123U)())
#endif
#ifndef OPEN_CFW_BLE_CALLBACK_CONTEXT
#define OPEN_CFW_BLE_CALLBACK_CONTEXT() \
    (((open_cfw_ble_callback_state_function)0x0046EFCDU)())
#endif
#ifndef OPEN_CFW_BLE_CALLBACK_ROLE
#define OPEN_CFW_BLE_CALLBACK_ROLE() \
    (((open_cfw_ble_callback_role_function)0x0046C631U)())
#endif
#ifndef OPEN_CFW_BLE_CALLBACK_ALLOCATE
#define OPEN_CFW_BLE_CALLBACK_ALLOCATE(size) \
    (((open_cfw_ble_callback_allocate_function)0x004BF99FU)(size))
#endif
#ifndef OPEN_CFW_BLE_CALLBACK_SEND
#define OPEN_CFW_BLE_CALLBACK_SEND(endpoint, packet) \
    (((open_cfw_ble_callback_send_function)0x004BF9BBU)( \
        (endpoint), (packet) \
    ))
#endif
#ifndef OPEN_CFW_BLE_CALLBACK_LOG_LEVEL
#define OPEN_CFW_BLE_CALLBACK_LOG_LEVEL() \
    (((open_cfw_ble_callback_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_BLE_CALLBACK_LOG
#define OPEN_CFW_BLE_CALLBACK_LOG(...) \
    (((open_cfw_ble_callback_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_CALLBACK_TRACE
#define OPEN_CFW_BLE_CALLBACK_TRACE(...) \
    (((open_cfw_ble_callback_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_ble_callback_pointer(unsigned int address)
{
    return (const void *)(open_cfw_ble_callback_uintptr)address;
}

static __attribute__((always_inline)) inline int
open_cfw_ble_callback_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_BLE_CALLBACK_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_BLE_CALLBACK_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline unsigned long long
open_cfw_ble_callback_return(
    unsigned int low,
    unsigned int high
)
{
    return (
        ((unsigned long long)high << 32)
        | (unsigned long long)low
    );
}

unsigned long long open_cfw_ble_connection_delayed_callback(
    unsigned int mode_argument,
    unsigned int return_low,
    unsigned int return_high,
    unsigned int diagnostic_argument
)
{
    unsigned char *controller = OPEN_CFW_BLE_CALLBACK_CONTROLLER();
    unsigned char mode = (unsigned char)mode_argument;
    const void *module =
        open_cfw_ble_callback_pointer(0x0078A0B8U);
    const void *file =
        open_cfw_ble_callback_pointer(0x006F81BCU);
    const void *function =
        open_cfw_ble_callback_pointer(0x0077DD44U);

    if (
        controller == (unsigned char *)0
        || controller[0x56] == 0U
    ) {
        if ((OPEN_CFW_BLE_CALLBACK_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_CALLBACK_LOG(
                1U,
                module,
                file,
                function,
                0x120U,
                open_cfw_ble_callback_pointer(0x00731604U),
                diagnostic_argument
            );
        }
        if (open_cfw_ble_callback_trace_enabled()) {
            const void *trace =
                open_cfw_ble_callback_pointer(0x007123E8U);

            OPEN_CFW_BLE_CALLBACK_TRACE(
                0x04000000U,
                trace,
                trace
            );
        }
        return open_cfw_ble_callback_return(return_low, return_high);
    }

    if (OPEN_CFW_BLE_CALLBACK_CONTEXT() == (unsigned char *)0) {
        if ((OPEN_CFW_BLE_CALLBACK_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_CALLBACK_LOG(
                2U,
                module,
                file,
                function,
                0x125U,
                open_cfw_ble_callback_pointer(0x00726B80U),
                diagnostic_argument
            );
        }
        if (open_cfw_ble_callback_trace_enabled()) {
            const void *trace =
                open_cfw_ble_callback_pointer(0x00708EE4U);

            OPEN_CFW_BLE_CALLBACK_TRACE(
                0x08000000U,
                trace,
                trace
            );
        }
        return open_cfw_ble_callback_return(return_low, return_high);
    }

    if (
        OPEN_CFW_BLE_CALLBACK_ROLE() == 1U
        && mode == 0xA4U
    ) {
        if ((OPEN_CFW_BLE_CALLBACK_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_CALLBACK_LOG(
                2U,
                module,
                file,
                function,
                0x12AU,
                open_cfw_ble_callback_pointer(0x00751CD4U),
                diagnostic_argument
            );
        }
        if (open_cfw_ble_callback_trace_enabled()) {
            const void *trace =
                open_cfw_ble_callback_pointer(0x00731634U);

            OPEN_CFW_BLE_CALLBACK_TRACE(
                0x08000000U,
                trace,
                trace
            );
        }
        return open_cfw_ble_callback_return(return_low, return_high);
    }

    {
        unsigned char *packet =
            (unsigned char *)OPEN_CFW_BLE_CALLBACK_ALLOCATE(12U);

        if (packet != (unsigned char *)0) {
            packet[2] = 0xB9U;
            *(unsigned short *)(void *)packet = 0U;
            *(unsigned short *)(void *)(packet + 8) = mode;
            OPEN_CFW_BLE_CALLBACK_SEND(controller[0x56], packet);
        }
    }
    return open_cfw_ble_callback_return(return_low, return_high);
}
