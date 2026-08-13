/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room product BLE registration/startup leaves reconstructed from
 * stock 0x004B7E74...0x004B8121, excluding the interposed GPIO vector.
 */

typedef __UINTPTR_TYPE__ open_cfw_app_ble_startup_uintptr;

#define OPEN_CFW_APP_BLE_CONTROL_ADDRESS 0x200727F0U
#define OPEN_CFW_APP_BLE_HANDLER_OFFSET 0x56U
#define OPEN_CFW_APP_BLE_RUNTIME_SMP_CONFIG 0x00774D44U
#define OPEN_CFW_APP_BLE_SMP_CONFIG_POINTER 0x200004B8U
#define OPEN_CFW_APP_BLE_RUNTIME_APP_CONFIG 0x0078C9A4U
#define OPEN_CFW_APP_BLE_APP_CONFIG_POINTER 0x20074358U
#define OPEN_CFW_APP_BLE_RUNTIME_STATE_ADDRESS 0x200737B0U
#define OPEN_CFW_APP_BLE_ADDRESS 0x200737BFU

#ifndef OPEN_CFW_APP_BLE_STARTUP_CONTROL
#define OPEN_CFW_APP_BLE_STARTUP_CONTROL \
    ((volatile unsigned char *)(open_cfw_app_ble_startup_uintptr) \
        OPEN_CFW_APP_BLE_CONTROL_ADDRESS)
#endif
#ifndef OPEN_CFW_APP_BLE_SMP_CONFIG_DESTINATION
#define OPEN_CFW_APP_BLE_SMP_CONFIG_DESTINATION \
    ((volatile unsigned int *)(open_cfw_app_ble_startup_uintptr) \
        OPEN_CFW_APP_BLE_SMP_CONFIG_POINTER)
#endif
#ifndef OPEN_CFW_APP_BLE_APP_CONFIG_DESTINATION
#define OPEN_CFW_APP_BLE_APP_CONFIG_DESTINATION \
    ((volatile unsigned int *)(open_cfw_app_ble_startup_uintptr) \
        OPEN_CFW_APP_BLE_APP_CONFIG_POINTER)
#endif
#ifndef OPEN_CFW_APP_BLE_RUNTIME_STATE
#define OPEN_CFW_APP_BLE_RUNTIME_STATE \
    ((volatile unsigned char *)(open_cfw_app_ble_startup_uintptr) \
        OPEN_CFW_APP_BLE_RUNTIME_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_APP_BLE_CALL0
typedef void (*open_cfw_app_ble_startup_call0_function)(void);
#define OPEN_CFW_APP_BLE_CALL0(address) \
    (((open_cfw_app_ble_startup_call0_function)((address) | 1U))())
#endif
#ifndef OPEN_CFW_APP_BLE_CALL1
typedef void (*open_cfw_app_ble_call1_function)(open_cfw_app_ble_startup_uintptr);
#define OPEN_CFW_APP_BLE_CALL1(address, argument0) \
    (((open_cfw_app_ble_call1_function)((address) | 1U))( \
        (open_cfw_app_ble_startup_uintptr)(argument0)))
#endif
#ifndef OPEN_CFW_APP_BLE_CALL2
typedef void (*open_cfw_app_ble_call2_function)(
    open_cfw_app_ble_startup_uintptr,
    open_cfw_app_ble_startup_uintptr
);
#define OPEN_CFW_APP_BLE_CALL2(address, argument0, argument1) \
    (((open_cfw_app_ble_call2_function)((address) | 1U))( \
        (open_cfw_app_ble_startup_uintptr)(argument0), \
        (open_cfw_app_ble_startup_uintptr)(argument1)))
#endif
#ifndef OPEN_CFW_APP_BLE_CALL3
typedef void (*open_cfw_app_ble_call3_function)(
    open_cfw_app_ble_startup_uintptr,
    open_cfw_app_ble_startup_uintptr,
    open_cfw_app_ble_startup_uintptr
);
#define OPEN_CFW_APP_BLE_CALL3(address, argument0, argument1, argument2) \
    (((open_cfw_app_ble_call3_function)((address) | 1U))( \
        (open_cfw_app_ble_startup_uintptr)(argument0), \
        (open_cfw_app_ble_startup_uintptr)(argument1), \
        (open_cfw_app_ble_startup_uintptr)(argument2)))
#endif

#ifndef OPEN_CFW_APP_BLE_HANDLER_ALLOCATE
typedef unsigned int (*open_cfw_app_ble_handler_allocate_function)(void *);
#define OPEN_CFW_APP_BLE_HANDLER_ALLOCATE(callback) \
    (((open_cfw_app_ble_handler_allocate_function)0x0052B981U)((callback)))
#endif

#ifndef OPEN_CFW_APP_BLE_BUFFER_INITIALIZE
typedef unsigned int (*open_cfw_app_ble_buffer_initialize_function)(
    unsigned int,
    void *,
    unsigned int,
    const void *
);
#define OPEN_CFW_APP_BLE_BUFFER_INITIALIZE(size, memory, count, descriptors) \
    (((open_cfw_app_ble_buffer_initialize_function)0x00530365U)( \
        (size), (memory), (count), (descriptors)))
#endif

#ifndef OPEN_CFW_APP_BLE_BUFFER_DIAGNOSTIC
#define OPEN_CFW_APP_BLE_BUFFER_DIAGNOSTIC(result) ((void)(result))
#endif

void open_cfw_app_ble_subsystem_initialize(void);
void open_cfw_app_ble_dm_callback(const void *event);
void open_cfw_app_ble_att_callback(const void *event);
void open_cfw_app_ble_ccc_callback(const void *event);
void open_cfw_app_ble_delayed_start_callback(void *message);

__attribute__((used, noinline))
void open_cfw_app_ble_handler_initialize(unsigned int handler_id)
{
    volatile unsigned char *control = OPEN_CFW_APP_BLE_STARTUP_CONTROL;
    volatile unsigned char *runtime_state = OPEN_CFW_APP_BLE_RUNTIME_STATE;

    control[OPEN_CFW_APP_BLE_HANDLER_OFFSET] = (unsigned char)handler_id;
    *OPEN_CFW_APP_BLE_SMP_CONFIG_DESTINATION = OPEN_CFW_APP_BLE_RUNTIME_SMP_CONFIG;
    *OPEN_CFW_APP_BLE_APP_CONFIG_DESTINATION = OPEN_CFW_APP_BLE_RUNTIME_APP_CONFIG;
    runtime_state[0] = 4U;
    OPEN_CFW_APP_BLE_CALL3(0x0046ED94U, handler_id, control, runtime_state);
    OPEN_CFW_APP_BLE_CALL3(0x00535488U, handler_id, control, runtime_state);
    OPEN_CFW_APP_BLE_CALL3(0x004A19F4U, handler_id, control, runtime_state);
    open_cfw_app_ble_subsystem_initialize();
}

__attribute__((used, noinline))
void open_cfw_app_ble_stack_register(void)
{
    OPEN_CFW_APP_BLE_CALL1(0x004D29CEU, open_cfw_app_ble_dm_callback);
    OPEN_CFW_APP_BLE_CALL2(0x004B6C64U, 3U, open_cfw_app_ble_dm_callback);
    OPEN_CFW_APP_BLE_CALL1(0x004B519EU, open_cfw_app_ble_att_callback);
    OPEN_CFW_APP_BLE_CALL1(0x004B51C8U, 0x005345ABU);
    OPEN_CFW_APP_BLE_CALL3(
        0x0052C224U,
        6U,
        0x007518C0U,
        open_cfw_app_ble_ccc_callback
    );
    OPEN_CFW_APP_BLE_CALL1(0x00532E7CU, 0x005355E1U);
    OPEN_CFW_APP_BLE_CALL2(0x0052DC1CU, 0x004B5B03U, 0x004B5ADDU);
    OPEN_CFW_APP_BLE_CALL0(0x0052DBF0U);
    OPEN_CFW_APP_BLE_CALL0(0x0053618CU);
    OPEN_CFW_APP_BLE_CALL2(0x005361C6U, 0U, 0x004BDC9DU);
    OPEN_CFW_APP_BLE_CALL0(0x005361BCU);
    OPEN_CFW_APP_BLE_CALL2(0x005361DEU, 0U, 0x004BDF3DU);
    OPEN_CFW_APP_BLE_CALL0(0x005361D4U);
    OPEN_CFW_APP_BLE_CALL2(0x005361F6U, 0U, 0x004BE2B5U);
    OPEN_CFW_APP_BLE_CALL0(0x005361ECU);
    OPEN_CFW_APP_BLE_CALL2(0x0053620EU, 0U, 0x004BE487U);
    OPEN_CFW_APP_BLE_CALL0(0x00536204U);
    OPEN_CFW_APP_BLE_CALL2(0x00536226U, 0U, 0x004BE7D3U);
    OPEN_CFW_APP_BLE_CALL0(0x0053621CU);
    OPEN_CFW_APP_BLE_CALL1(0x004B5A3AU, 0U);
}

__attribute__((used, noinline))
void open_cfw_app_ble_stack_initialize(void)
{
    unsigned int handler;
    unsigned int buffer_result;

    OPEN_CFW_APP_BLE_CALL0(0x0052B9B2U);
    OPEN_CFW_APP_BLE_CALL0(0x0052A474U);
    buffer_result = OPEN_CFW_APP_BLE_BUFFER_INITIALIZE(
        0x2940U,
        (void *)(open_cfw_app_ble_startup_uintptr)0x2004FA98U,
        4U,
        (const void *)(open_cfw_app_ble_startup_uintptr)0x200003B0U
    );
    if ((unsigned short)buffer_result >= 0x2941U) {
        OPEN_CFW_APP_BLE_BUFFER_DIAGNOSTIC(
            (unsigned short)buffer_result - 0x2940U
        );
    }
    OPEN_CFW_APP_BLE_CALL0(0x00536324U);
    OPEN_CFW_APP_BLE_CALL0(0x0053648EU);
    OPEN_CFW_APP_BLE_CALL0(0x005366CCU);
    OPEN_CFW_APP_BLE_CALL0(0x005367CAU);

    handler = OPEN_CFW_APP_BLE_HANDLER_ALLOCATE((void *)0x00536815U);
    OPEN_CFW_APP_BLE_CALL1(0x005367F8U, (unsigned char)handler);
    handler = OPEN_CFW_APP_BLE_HANDLER_ALLOCATE((void *)0x004D2A5DU);
    OPEN_CFW_APP_BLE_CALL1(0x004B308CU, 0U);
    OPEN_CFW_APP_BLE_CALL0(0x004BAC2CU);
    OPEN_CFW_APP_BLE_CALL0(0x005369EAU);
    OPEN_CFW_APP_BLE_CALL0(0x004C584AU);
    OPEN_CFW_APP_BLE_CALL0(0x004B6C28U);
    OPEN_CFW_APP_BLE_CALL0(0x00536A98U);
    OPEN_CFW_APP_BLE_CALL0(0x00536B18U);
    OPEN_CFW_APP_BLE_CALL0(0x004D250CU);
    OPEN_CFW_APP_BLE_CALL0(0x0053496AU);
    OPEN_CFW_APP_BLE_CALL0(0x004D27E0U);
    OPEN_CFW_APP_BLE_CALL1(0x004D2A46U, (unsigned char)handler);

    handler = OPEN_CFW_APP_BLE_HANDLER_ALLOCATE((void *)0x00536FA5U);
    OPEN_CFW_APP_BLE_CALL1(0x00536F6AU, (unsigned char)handler);
    OPEN_CFW_APP_BLE_CALL0(0x00530B34U);
    OPEN_CFW_APP_BLE_CALL0(0x00536E78U);
    OPEN_CFW_APP_BLE_CALL0(0x00537200U);

    handler = OPEN_CFW_APP_BLE_HANDLER_ALLOCATE((void *)0x004B5147U);
    OPEN_CFW_APP_BLE_CALL1(0x004B511EU, (unsigned char)handler);
    OPEN_CFW_APP_BLE_CALL0(0x005351DCU);
    OPEN_CFW_APP_BLE_CALL0(0x00533E40U);
    OPEN_CFW_APP_BLE_CALL0(0x00531B1CU);

    handler = OPEN_CFW_APP_BLE_HANDLER_ALLOCATE((void *)0x00537D0DU);
    OPEN_CFW_APP_BLE_CALL1(0x00537CB2U, (unsigned char)handler);
    OPEN_CFW_APP_BLE_CALL0(0x00537EECU);
    OPEN_CFW_APP_BLE_CALL0(0x00537F14U);
    OPEN_CFW_APP_BLE_CALL0(0x005380DCU);
    OPEN_CFW_APP_BLE_CALL0(0x00538104U);
    OPEN_CFW_APP_BLE_CALL1(0x0052ACCEU, 251U);

    handler = OPEN_CFW_APP_BLE_HANDLER_ALLOCATE((void *)0x004BAE85U);
    OPEN_CFW_APP_BLE_CALL1(0x004BAE6CU, (unsigned char)handler);
    handler = OPEN_CFW_APP_BLE_HANDLER_ALLOCATE((void *)0x004B7D33U);
    open_cfw_app_ble_handler_initialize((unsigned char)handler);
    handler = OPEN_CFW_APP_BLE_HANDLER_ALLOCATE((void *)0x004B4AB3U);
    OPEN_CFW_APP_BLE_CALL1(0x004B4A7CU, (unsigned char)handler);
}

__attribute__((used, noinline))
const unsigned char *open_cfw_app_ble_address_get(void)
{
#ifdef OPEN_CFW_APP_BLE_ADDRESS_POINTER
    return OPEN_CFW_APP_BLE_ADDRESS_POINTER;
#else
    return (const unsigned char *)(open_cfw_app_ble_startup_uintptr)
        OPEN_CFW_APP_BLE_ADDRESS;
#endif
}

__attribute__((used, noinline))
void open_cfw_app_ble_start(void)
{
    OPEN_CFW_APP_BLE_CALL0(0x004B73E8U);
    OPEN_CFW_APP_BLE_CALL0(0x004B49CEU);
    OPEN_CFW_APP_BLE_CALL1(0x00491102U, 100U);
    OPEN_CFW_APP_BLE_CALL1(0x004B48A6U, 0U);
    open_cfw_app_ble_stack_initialize();
    open_cfw_app_ble_stack_register();
    OPEN_CFW_APP_BLE_CALL0(0x004B3026U);
    OPEN_CFW_APP_BLE_CALL3(
        0x0047697EU,
        open_cfw_app_ble_delayed_start_callback,
        0U,
        10000U
    );
}
