#ifndef OPEN_CFW_TEST_BLE_WSF_HOST_H
#define OPEN_CFW_TEST_BLE_WSF_HOST_H

typedef struct {
    unsigned int reserved_0;
    unsigned int reserved_4;
    unsigned int thread;
    unsigned int reserved_c;
    unsigned int reserved_10;
    unsigned int tx_ready;
} open_cfw_test_ble_wsf_state;

extern open_cfw_test_ble_wsf_state open_cfw_test_ble_wsf_state_words;

void *open_cfw_test_ble_wsf_semaphore_new(
    unsigned int maximum,
    unsigned int initial,
    const void *attributes
);
void open_cfw_test_ble_wsf_fatal(void);
void open_cfw_test_ble_wsf_resource_initialize(void);
void open_cfw_test_ble_wsf_resource_deinitialize(void);
void open_cfw_test_ble_wsf_app_start(void);
void open_cfw_test_ble_wsf_dispatcher(void);
void open_cfw_test_ble_wsf_stage_enter(unsigned int index);
void open_cfw_test_ble_wsf_stage_ready(unsigned int index);
void *open_cfw_test_ble_wsf_thread_new(
    void (*entry)(void *),
    void *argument,
    const void *attributes
);
void open_cfw_test_ble_wsf_thread_terminate(void *thread);
int open_cfw_test_ble_wsf_semaphore_acquire(void *semaphore, unsigned int timeout);
unsigned int open_cfw_test_ble_wsf_kernel_tick(void);
unsigned int open_cfw_test_ble_wsf_delay(unsigned int ticks);
unsigned int open_cfw_test_ble_wsf_semaphore_count(void *semaphore);
int open_cfw_test_ble_wsf_semaphore_release(void *semaphore);
void open_cfw_test_ble_wsf_resource_diagnostic(
    unsigned int maximum,
    unsigned int initial
);
void open_cfw_test_ble_wsf_wait_bound_diagnostic(void);
void open_cfw_test_ble_wsf_wait_result_diagnostic(
    unsigned int elapsed,
    unsigned int retries
);
void open_cfw_test_ble_wsf_release_failure_diagnostic(
    int status,
    unsigned int count
);
void open_cfw_test_ble_wsf_already_full_diagnostic(unsigned int count);
unsigned int open_cfw_test_ble_wsf_task_loop_continue(void);

#define OPEN_CFW_BLE_WSF_TASK_STATE ((void *)&open_cfw_test_ble_wsf_state_words)
#define OPEN_CFW_BLE_WSF_LIFECYCLE_STATE \
    ((void *)&open_cfw_test_ble_wsf_state_words)
#define OPEN_CFW_BLE_WSF_FLOW_STATE ((void *)&open_cfw_test_ble_wsf_state_words)
#define OPEN_CFW_BLE_WSF_SEMAPHORE_NEW(maximum, initial, attributes) \
    open_cfw_test_ble_wsf_semaphore_new((maximum), (initial), (attributes))
#define OPEN_CFW_BLE_WSF_FATAL() open_cfw_test_ble_wsf_fatal()
#define OPEN_CFW_BLE_WSF_THREAD_FATAL() open_cfw_test_ble_wsf_fatal()
#define OPEN_CFW_BLE_WSF_RESOURCE_INITIALIZE() \
    open_cfw_test_ble_wsf_resource_initialize()
#define OPEN_CFW_BLE_WSF_RESOURCE_DEINITIALIZE() \
    open_cfw_test_ble_wsf_resource_deinitialize()
#define OPEN_CFW_BLE_WSF_APP_START() open_cfw_test_ble_wsf_app_start()
#define OPEN_CFW_BLE_WSF_DISPATCHER() open_cfw_test_ble_wsf_dispatcher()
#define OPEN_CFW_BLE_WSF_STAGE_ENTER_BACKEND(index) \
    open_cfw_test_ble_wsf_stage_enter((index))
#define OPEN_CFW_BLE_WSF_STAGE_READY_BACKEND(index) \
    open_cfw_test_ble_wsf_stage_ready((index))
#define OPEN_CFW_BLE_WSF_THREAD_NEW(entry, argument, attributes) \
    open_cfw_test_ble_wsf_thread_new((entry), (argument), (attributes))
#define OPEN_CFW_BLE_WSF_THREAD_TERMINATE(thread) \
    open_cfw_test_ble_wsf_thread_terminate((thread))
#define OPEN_CFW_BLE_WSF_SEMAPHORE_ACQUIRE(semaphore, timeout) \
    open_cfw_test_ble_wsf_semaphore_acquire((semaphore), (timeout))
#define OPEN_CFW_BLE_WSF_KERNEL_TICK() open_cfw_test_ble_wsf_kernel_tick()
#define OPEN_CFW_BLE_WSF_DELAY(ticks) open_cfw_test_ble_wsf_delay((ticks))
#define OPEN_CFW_BLE_WSF_SEMAPHORE_COUNT(semaphore) \
    open_cfw_test_ble_wsf_semaphore_count((semaphore))
#define OPEN_CFW_BLE_WSF_SEMAPHORE_RELEASE(semaphore) \
    open_cfw_test_ble_wsf_semaphore_release((semaphore))
#define OPEN_CFW_BLE_WSF_RESOURCE_DIAGNOSTIC(maximum, initial) \
    open_cfw_test_ble_wsf_resource_diagnostic((maximum), (initial))
#define OPEN_CFW_BLE_WSF_WAIT_BOUND_DIAGNOSTIC() \
    open_cfw_test_ble_wsf_wait_bound_diagnostic()
#define OPEN_CFW_BLE_WSF_WAIT_RESULT_DIAGNOSTIC(elapsed, retries) \
    open_cfw_test_ble_wsf_wait_result_diagnostic((elapsed), (retries))
#define OPEN_CFW_BLE_WSF_RELEASE_FAILURE_DIAGNOSTIC(status, count) \
    open_cfw_test_ble_wsf_release_failure_diagnostic((status), (count))
#define OPEN_CFW_BLE_WSF_ALREADY_FULL_DIAGNOSTIC(count) \
    open_cfw_test_ble_wsf_already_full_diagnostic((count))
#define OPEN_CFW_BLE_WSF_TASK_LOOP_CONTINUE() \
    open_cfw_test_ble_wsf_task_loop_continue()

#endif
