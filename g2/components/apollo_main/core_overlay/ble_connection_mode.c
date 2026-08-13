/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded BLE connection-parameter mode selectors matched to stock entries
 * 0x00476DB8 and 0x00476FE2.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_mode_uintptr;

typedef unsigned int (*open_cfw_ble_mode_log_level_function)(void);
typedef void (*open_cfw_ble_mode_log_function)(
    unsigned int,
    const void *,
    const void *,
    const void *,
    unsigned int,
    const void *,
    ...
);
typedef void (*open_cfw_ble_mode_trace_function)(
    unsigned int,
    const void *,
    const void *,
    ...
);

#ifndef OPEN_CFW_BLE_MODE_DEFAULTS
#define OPEN_CFW_BLE_MODE_DEFAULTS \
    (*(const volatile unsigned short *volatile *)0x2007435CU)
#endif
#ifndef OPEN_CFW_BLE_MODE_LOG_LEVEL
#define OPEN_CFW_BLE_MODE_LOG_LEVEL() \
    (((open_cfw_ble_mode_log_level_function)0x0043D0CFU)())
#endif
#ifndef OPEN_CFW_BLE_MODE_LOG
#define OPEN_CFW_BLE_MODE_LOG(...) \
    (((open_cfw_ble_mode_log_function)0x0043D575U)(__VA_ARGS__))
#endif
#ifndef OPEN_CFW_BLE_MODE_TRACE
#define OPEN_CFW_BLE_MODE_TRACE(...) \
    (((open_cfw_ble_mode_trace_function)0x0043CE9FU)(__VA_ARGS__))
#endif

static __attribute__((always_inline)) inline const void *
open_cfw_ble_mode_pointer(unsigned int address)
{
    return (const void *)(open_cfw_ble_mode_uintptr)address;
}

static __attribute__((always_inline)) inline int
open_cfw_ble_mode_trace_enabled(void)
{
    unsigned int level = OPEN_CFW_BLE_MODE_LOG_LEVEL();

    if ((level & 1U) != 0U) {
        return 1;
    }
    return (OPEN_CFW_BLE_MODE_LOG_LEVEL() & 4U) != 0U;
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_ble_mode_select(
    const volatile unsigned short *state,
    const void *function,
    unsigned int first_line,
    unsigned int interval_line,
    unsigned int latency_line,
    unsigned int timeout_line,
    unsigned int short_line,
    unsigned int long_line,
    unsigned int threshold
)
{
    const volatile unsigned short *defaults = OPEN_CFW_BLE_MODE_DEFAULTS;
    const void *module = open_cfw_ble_mode_pointer(0x0077774CU);
    const void *file = open_cfw_ble_mode_pointer(0x00777748U);

    if ((OPEN_CFW_BLE_MODE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_MODE_LOG(
            4U,
            module,
            file,
            function,
            first_line,
            open_cfw_ble_mode_pointer(0x00777760U),
            state[12],
            state[12],
            state[13],
            defaults[2],
            defaults[3],
            defaults[4]
        );
    }
    if (open_cfw_ble_mode_trace_enabled()) {
        const void *trace = open_cfw_ble_mode_pointer(0x00777768U);

        OPEN_CFW_BLE_MODE_TRACE(
            0x11800000U,
            trace,
            trace,
            state[12],
            state[12],
            state[13],
            defaults[2],
            defaults[3],
            defaults[4]
        );
    }

    if ((OPEN_CFW_BLE_MODE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_MODE_LOG(
            4U,
            module,
            file,
            function,
            interval_line,
            open_cfw_ble_mode_pointer(0x0077776CU),
            ((unsigned int)state[12] * 0x4E2U) / 1000U,
            0x18U
        );
    }
    if (open_cfw_ble_mode_trace_enabled()) {
        const void *trace = open_cfw_ble_mode_pointer(0x00777770U);

        OPEN_CFW_BLE_MODE_TRACE(
            0x10800000U,
            trace,
            trace,
            ((unsigned int)state[12] * 0x4E2U) / 1000U,
            0x18U
        );
    }

    if ((OPEN_CFW_BLE_MODE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_MODE_LOG(
            4U,
            module,
            file,
            function,
            latency_line,
            open_cfw_ble_mode_pointer(0x00777A6CU),
            state[13]
        );
    }
    if (open_cfw_ble_mode_trace_enabled()) {
        const void *trace = open_cfw_ble_mode_pointer(0x00777A70U);

        OPEN_CFW_BLE_MODE_TRACE(
            0x10400000U,
            trace,
            trace,
            state[13]
        );
    }

    if ((OPEN_CFW_BLE_MODE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_MODE_LOG(
            4U,
            module,
            file,
            function,
            timeout_line,
            open_cfw_ble_mode_pointer(0x00777A74U),
            ((unsigned int)state[14] * 10000U) / 1000U
        );
    }
    if (open_cfw_ble_mode_trace_enabled()) {
        const void *trace = open_cfw_ble_mode_pointer(0x00777A78U);

        OPEN_CFW_BLE_MODE_TRACE(
            0x10400000U,
            trace,
            trace,
            ((unsigned int)state[14] * 10000U) / 1000U
        );
    }

    if (state[12] < threshold) {
        if ((OPEN_CFW_BLE_MODE_LOG_LEVEL() & 2U) != 0U) {
            OPEN_CFW_BLE_MODE_LOG(
                4U,
                module,
                file,
                function,
                short_line,
                open_cfw_ble_mode_pointer(0x00777A7CU)
            );
        }
        if (open_cfw_ble_mode_trace_enabled()) {
            const void *trace = open_cfw_ble_mode_pointer(0x00777A80U);

            OPEN_CFW_BLE_MODE_TRACE(0x10000000U, trace, trace);
        }
        return 0xA3U;
    }

    if ((OPEN_CFW_BLE_MODE_LOG_LEVEL() & 2U) != 0U) {
        OPEN_CFW_BLE_MODE_LOG(
            4U,
            module,
            file,
            function,
            long_line,
            open_cfw_ble_mode_pointer(0x00777A84U)
        );
    }
    if (open_cfw_ble_mode_trace_enabled()) {
        const void *trace = open_cfw_ble_mode_pointer(0x00777A88U);

        OPEN_CFW_BLE_MODE_TRACE(0x10000000U, trace, trace);
    }
    return 0xA4U;
}

unsigned int open_cfw_ble_connection_select_primary(
    const volatile unsigned short *state
)
{
    return open_cfw_ble_mode_select(
        state,
        open_cfw_ble_mode_pointer(0x00777764U),
        0xC6U,
        0xC9U,
        0xCAU,
        0xCBU,
        0xCEU,
        0xD1U,
        0x19U
    );
}

unsigned int open_cfw_ble_connection_select_secondary(
    const volatile unsigned short *state
)
{
    return open_cfw_ble_mode_select(
        state,
        open_cfw_ble_mode_pointer(0x00777A8CU),
        0xD7U,
        0xDAU,
        0xDBU,
        0xDCU,
        0xE2U,
        0xDFU,
        0x48U
    );
}
