#ifndef OPEN_CFW_TEST_BLE_MSGRX_HOST_H
#define OPEN_CFW_TEST_BLE_MSGRX_HOST_H

#include <stddef.h>

extern unsigned int open_cfw_test_ble_msgrx_state_words[4];

void *open_cfw_test_ble_msgrx_queue_new(
    unsigned int count,
    unsigned int size,
    const void *attributes
);
void open_cfw_test_ble_msgrx_failure(void);
void open_cfw_test_ble_msgrx_stage_enter(unsigned int index);
void open_cfw_test_ble_msgrx_stage_ready(unsigned int index);
void *open_cfw_test_ble_msgrx_thread_new(
    void *entry,
    void *argument,
    const void *attributes
);
void open_cfw_test_ble_msgrx_thread_terminate(void *thread);
unsigned int open_cfw_test_ble_msgrx_queue_get(
    void *queue,
    void *record,
    unsigned char *priority,
    unsigned int timeout
);
unsigned int open_cfw_test_ble_msgrx_queue_count(void *queue);
unsigned int open_cfw_test_ble_msgrx_queue_capacity(void *queue);
unsigned int open_cfw_test_ble_msgrx_queue_put(
    void *queue,
    const void *record,
    unsigned char priority,
    unsigned int timeout
);
unsigned int open_cfw_test_ble_msgrx_flags_set(
    void *thread,
    unsigned int flags
);
void *open_cfw_test_ble_msgrx_allocate(unsigned int size);
void open_cfw_test_ble_msgrx_free(void *pointer);
void *open_cfw_test_ble_msgrx_memset(void *destination, int value, size_t size);
void *open_cfw_test_ble_msgrx_memcpy(
    void *destination,
    const void *source,
    size_t size
);
void open_cfw_test_ble_msgrx_route_80(const void *payload, unsigned int length);
void open_cfw_test_ble_msgrx_route_c0(
    unsigned int type,
    const void *payload,
    unsigned int length
);
void open_cfw_test_ble_msgrx_route_c4(
    unsigned int type,
    const void *payload,
    unsigned int length
);
void open_cfw_test_ble_msgrx_route_200(
    unsigned int selector,
    const void *payload
);
void open_cfw_test_ble_msgrx_route_400(void);
void open_cfw_test_ble_msgrx_hexdump(const void *payload, unsigned int length);
unsigned int open_cfw_test_ble_msgrx_wait(
    unsigned int flags,
    unsigned int options,
    unsigned int timeout
);
int open_cfw_test_ble_msgrx_loop_continue(void);

#define OPEN_CFW_BLE_MSGRX_RUNTIME_STATE \
    ((volatile open_cfw_ble_msgrx_runtime_state *) \
        open_cfw_test_ble_msgrx_state_words)
#define OPEN_CFW_BLE_MSGRX_LIFECYCLE_STATE \
    ((volatile open_cfw_ble_msgrx_lifecycle_state *) \
        open_cfw_test_ble_msgrx_state_words)
#define OPEN_CFW_BLE_MSGRX_DISPATCH_STATE \
    ((volatile open_cfw_ble_msgrx_dispatch_state *) \
        open_cfw_test_ble_msgrx_state_words)
#define OPEN_CFW_BLE_MSGRX_ENQUEUE_STATE \
    ((volatile open_cfw_ble_msgrx_enqueue_state *) \
        open_cfw_test_ble_msgrx_state_words)
#define OPEN_CFW_BLE_MSGRX_QUEUE_NEW \
    open_cfw_test_ble_msgrx_queue_new
#define OPEN_CFW_BLE_MSGRX_QUEUE_FAILURE() \
    open_cfw_test_ble_msgrx_failure()
#define OPEN_CFW_BLE_MSGRX_STAGE_ENTER_BACKEND \
    open_cfw_test_ble_msgrx_stage_enter
#define OPEN_CFW_BLE_MSGRX_STAGE_READY_BACKEND \
    open_cfw_test_ble_msgrx_stage_ready
#define OPEN_CFW_BLE_MSGRX_THREAD_NEW \
    open_cfw_test_ble_msgrx_thread_new
#define OPEN_CFW_BLE_MSGRX_THREAD_TERMINATE \
    open_cfw_test_ble_msgrx_thread_terminate
#define OPEN_CFW_BLE_MSGRX_THREAD_FAILURE() \
    open_cfw_test_ble_msgrx_failure()
#define OPEN_CFW_BLE_MSGRX_QUEUE_GET \
    open_cfw_test_ble_msgrx_queue_get
#define OPEN_CFW_BLE_MSGRX_QUEUE_COUNT \
    open_cfw_test_ble_msgrx_queue_count
#define OPEN_CFW_BLE_MSGRX_QUEUE_CAPACITY \
    open_cfw_test_ble_msgrx_queue_capacity
#define OPEN_CFW_BLE_MSGRX_QUEUE_PUT \
    open_cfw_test_ble_msgrx_queue_put
#define OPEN_CFW_BLE_MSGRX_THREAD_FLAGS_SET \
    open_cfw_test_ble_msgrx_flags_set
#define OPEN_CFW_BLE_MSGRX_ALLOCATE \
    open_cfw_test_ble_msgrx_allocate
#define OPEN_CFW_BLE_MSGRX_FREE \
    open_cfw_test_ble_msgrx_free
#define OPEN_CFW_BLE_MSGRX_MEMSET \
    open_cfw_test_ble_msgrx_memset
#define OPEN_CFW_BLE_MSGRX_MEMCPY \
    open_cfw_test_ble_msgrx_memcpy
#define OPEN_CFW_BLE_MSGRX_ROUTE_80 \
    open_cfw_test_ble_msgrx_route_80
#define OPEN_CFW_BLE_MSGRX_ROUTE_C0 \
    open_cfw_test_ble_msgrx_route_c0
#define OPEN_CFW_BLE_MSGRX_ROUTE_C4 \
    open_cfw_test_ble_msgrx_route_c4
#define OPEN_CFW_BLE_MSGRX_ROUTE_200 \
    open_cfw_test_ble_msgrx_route_200
#define OPEN_CFW_BLE_MSGRX_ROUTE_400() \
    open_cfw_test_ble_msgrx_route_400()
#define OPEN_CFW_BLE_MSGRX_HEXDUMP \
    open_cfw_test_ble_msgrx_hexdump
#define OPEN_CFW_BLE_MSGRX_WAIT \
    open_cfw_test_ble_msgrx_wait
#define OPEN_CFW_BLE_MSGRX_LOOP_CONTINUE() \
    open_cfw_test_ble_msgrx_loop_continue()

#endif
