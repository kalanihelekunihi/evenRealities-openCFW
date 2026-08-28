/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room BLE message-receive thread entry reconstructed from stock
 * 0x0048EDB0...0x0048EE27.
 */

#define OPEN_CFW_BLE_MSGRX_THREAD_FLAGS 0x00FFFFFFU
#define OPEN_CFW_BLE_MSGRX_WAIT_FOREVER 0xFFFFFFFFU
#define OPEN_CFW_BLE_MSGRX_FLAG_ERROR 0x80000000U

typedef unsigned int (*open_cfw_ble_msgrx_wait_function)(
    unsigned int,
    unsigned int,
    unsigned int
);

void open_cfw_ble_msgrx_stage_enter(void);
void open_cfw_ble_msgrx_queue_initialize(void);
void open_cfw_ble_msgrx_application_initialize(void);
void open_cfw_ble_msgrx_thread_initialize(void);
void open_cfw_ble_msgrx_stage_ready(void);
void open_cfw_ble_msgrx_dispatch_flags(unsigned int flags);

#ifndef OPEN_CFW_BLE_MSGRX_WAIT
#define OPEN_CFW_BLE_MSGRX_WAIT(flags, options, timeout) \
    (((open_cfw_ble_msgrx_wait_function)0x004492C3U)( \
        (flags), (options), (timeout)))
#endif

#ifndef OPEN_CFW_BLE_MSGRX_LOOP_CONTINUE
#define OPEN_CFW_BLE_MSGRX_LOOP_CONTINUE() 1
#endif

__attribute__((used, noinline))
void open_cfw_ble_msgrx_thread(void *argument)
{
    unsigned int flags;

    (void)argument;
    open_cfw_ble_msgrx_stage_enter();
    open_cfw_ble_msgrx_queue_initialize();
    open_cfw_ble_msgrx_application_initialize();
    open_cfw_ble_msgrx_thread_initialize();
    open_cfw_ble_msgrx_stage_ready();

    for (;;) {
        flags = OPEN_CFW_BLE_MSGRX_WAIT(
            OPEN_CFW_BLE_MSGRX_THREAD_FLAGS,
            0U,
            OPEN_CFW_BLE_MSGRX_WAIT_FOREVER
        );
        while (flags != 0U && flags < OPEN_CFW_BLE_MSGRX_FLAG_ERROR) {
            open_cfw_ble_msgrx_dispatch_flags(flags);
            flags = OPEN_CFW_BLE_MSGRX_WAIT(
                OPEN_CFW_BLE_MSGRX_THREAD_FLAGS,
                0U,
                OPEN_CFW_BLE_MSGRX_WAIT_FOREVER
            );
        }
        if (!OPEN_CFW_BLE_MSGRX_LOOP_CONTINUE()) {
            return;
        }
    }
}
