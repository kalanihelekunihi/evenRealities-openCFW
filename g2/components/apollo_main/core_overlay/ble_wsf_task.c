/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room BLE WSF task and resource initialization reconstructed from
 * stock 0x004D0A4C...0x004D0AF5.
 */

typedef __UINTPTR_TYPE__ open_cfw_ble_wsf_task_uintptr;

#define OPEN_CFW_BLE_WSF_STATE_ADDRESS 0x20004068U
#define OPEN_CFW_BLE_WSF_STAGE_INDEX 9U

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int reserved_c;
    unsigned int reserved_10;
    unsigned int tx_ready;
} open_cfw_ble_wsf_task_state;

#ifndef OPEN_CFW_BLE_WSF_TASK_STATE
#define OPEN_CFW_BLE_WSF_TASK_STATE \
    ((volatile open_cfw_ble_wsf_task_state *) \
        (open_cfw_ble_wsf_task_uintptr)OPEN_CFW_BLE_WSF_STATE_ADDRESS)
#endif

#ifndef OPEN_CFW_BLE_WSF_STAGE_ENTER_BACKEND
typedef void (*open_cfw_ble_wsf_stage_function)(unsigned int);
#define OPEN_CFW_BLE_WSF_STAGE_ENTER_BACKEND(index) \
    (((open_cfw_ble_wsf_stage_function)0x004C9B87U)((index)))
#endif

#ifndef OPEN_CFW_BLE_WSF_STAGE_READY_BACKEND
#define OPEN_CFW_BLE_WSF_STAGE_READY_BACKEND(index) \
    (((open_cfw_ble_wsf_stage_function)0x004C9BE3U)((index)))
#endif

#ifndef OPEN_CFW_BLE_WSF_SEMAPHORE_NEW
typedef void *(*open_cfw_ble_wsf_semaphore_new_function)(
    unsigned int,
    unsigned int,
    const void *
);
#define OPEN_CFW_BLE_WSF_SEMAPHORE_NEW(maximum, initial, attributes) \
    (((open_cfw_ble_wsf_semaphore_new_function)0x0044989BU)( \
        (maximum), (initial), (attributes)))
#endif

#ifndef OPEN_CFW_BLE_WSF_FATAL
typedef void (*open_cfw_ble_wsf_fatal_function)(void);
#define OPEN_CFW_BLE_WSF_FATAL() \
    do { \
        ((open_cfw_ble_wsf_fatal_function)0x005FA0A5U)(); \
        *(volatile unsigned int *)(open_cfw_ble_wsf_task_uintptr) \
            0xFFFFFFFFU = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_BLE_WSF_RESOURCE_INITIALIZE
typedef void (*open_cfw_ble_wsf_resource_function)(void);
#define OPEN_CFW_BLE_WSF_RESOURCE_INITIALIZE() \
    (((open_cfw_ble_wsf_resource_function)0x004ABCB1U)())
#endif

#ifndef OPEN_CFW_BLE_WSF_APP_START
typedef void (*open_cfw_ble_wsf_app_start_function)(void);
#define OPEN_CFW_BLE_WSF_APP_START() \
    (((open_cfw_ble_wsf_app_start_function)0x004B80F1U)())
#endif

#ifndef OPEN_CFW_BLE_WSF_DISPATCHER
typedef void (*open_cfw_ble_wsf_dispatcher_function)(void);
#define OPEN_CFW_BLE_WSF_DISPATCHER() \
    (((open_cfw_ble_wsf_dispatcher_function)0x0052B9D1U)())
#endif

#ifndef OPEN_CFW_BLE_WSF_TASK_LOOP_CONTINUE
#define OPEN_CFW_BLE_WSF_TASK_LOOP_CONTINUE() 1
#endif

#ifndef OPEN_CFW_BLE_WSF_RESOURCE_DIAGNOSTIC
#define OPEN_CFW_BLE_WSF_RESOURCE_DIAGNOSTIC(maximum, initial) ((void)0)
#endif

void open_cfw_ble_wsf_resource_initialize(void);
void open_cfw_ble_wsf_start(void);
void open_cfw_ble_wsf_loop_initialize(void);
void open_cfw_ble_wsf_enter(void);
void open_cfw_ble_wsf_ready(void);

__attribute__((used, noinline))
void open_cfw_ble_wsf_task(void *argument)
{
    (void)argument;
    open_cfw_ble_wsf_enter();
    open_cfw_ble_wsf_resource_initialize();
    open_cfw_ble_wsf_start();
    open_cfw_ble_wsf_loop_initialize();
    open_cfw_ble_wsf_ready();
    do {
        OPEN_CFW_BLE_WSF_DISPATCHER();
    } while (OPEN_CFW_BLE_WSF_TASK_LOOP_CONTINUE());
}

__attribute__((used, noinline))
void open_cfw_ble_wsf_start(void)
{
    OPEN_CFW_BLE_WSF_APP_START();
}

__attribute__((used, noinline))
void open_cfw_ble_wsf_resource_initialize(void)
{
    volatile open_cfw_ble_wsf_task_state *state = OPEN_CFW_BLE_WSF_TASK_STATE;

    state->tx_ready = (unsigned int)(open_cfw_ble_wsf_task_uintptr)
        OPEN_CFW_BLE_WSF_SEMAPHORE_NEW(1U, 1U, (const void *)0);
    if (state->tx_ready == 0U) {
        OPEN_CFW_BLE_WSF_FATAL();
        return;
    }
    OPEN_CFW_BLE_WSF_RESOURCE_DIAGNOSTIC(1U, 1U);
    OPEN_CFW_BLE_WSF_RESOURCE_INITIALIZE();
}

__attribute__((used, noinline))
void open_cfw_ble_wsf_loop_initialize(void)
{
}

__attribute__((used, noinline))
void open_cfw_ble_wsf_enter(void)
{
    OPEN_CFW_BLE_WSF_STAGE_ENTER_BACKEND(OPEN_CFW_BLE_WSF_STAGE_INDEX);
}

__attribute__((used, noinline))
void open_cfw_ble_wsf_ready(void)
{
    OPEN_CFW_BLE_WSF_STAGE_READY_BACKEND(OPEN_CFW_BLE_WSF_STAGE_INDEX);
}
