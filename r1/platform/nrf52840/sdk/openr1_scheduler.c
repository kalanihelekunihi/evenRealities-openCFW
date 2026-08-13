#include "openr1_scheduler.h"

#include <stddef.h>

#include "cmsis_os2.h"
#include "FreeRTOS.h"
#include "nrf_error.h"
#include "nrf_sdh.h"
#include "task.h"
#include "timers.h"
#include "SEGGER_RTT.h"

#include "openr1_bae8.h"
#include "openr1_watchdog.h"

#define OPENR1_SOFTDEVICE_WAKE_FLAG UINT32_C(0x00000001)

extern r1_runtime *openr1_platform_runtime(void);

static osThreadId_t channel1_thread;
static osThreadId_t runtime_thread;
static osThreadId_t softdevice_thread;
static osMessageQueueId_t channel1_queue;
static osMessageQueueId_t shared_queue;
static osSemaphoreId_t glasses_credits;
static osSemaphoreId_t phone_credits;
static openr1_startup_fn platform_startup;

static StaticTask_t channel1_control_block;
static StaticTask_t runtime_control_block;
static StaticTask_t softdevice_control_block;
static StaticTask_t idle_control_block;
static StaticTask_t timer_control_block;
static StackType_t channel1_stack[configMINIMAL_STACK_SIZE];
static StackType_t runtime_stack[configMINIMAL_STACK_SIZE];
static StackType_t softdevice_stack[configMINIMAL_STACK_SIZE];
static StackType_t idle_stack[configMINIMAL_STACK_SIZE];
static StackType_t timer_stack[configTIMER_TASK_STACK_DEPTH];

static void send_channel1(const r1_tx_event *event) {
    const bool acquired = osSemaphoreAcquire(
        glasses_credits, R1_TX_ENQUEUE_WAIT_TICKS) == osOK;
    const r1_tx_status status = openr1_bae8_transmit(event);
    r1_bae8_hvx_retry_plan plan;
    if (r1_bae8_plan_hvx_result(
            false, acquired, status, 0u, &plan) == R1_OK &&
        plan.release_credit) {
        (void)osSemaphoreRelease(glasses_credits);
    }
}

static void send_eus(const r1_tx_event *event) {
    if (osSemaphoreAcquire(phone_credits, R1_EUS_CREDIT_WAIT_TICKS) != osOK) {
        return;
    }
    r1_tx_status status = openr1_bae8_transmit(event);
    r1_bae8_hvx_retry_plan plan;
    if (r1_bae8_plan_hvx_result(
            true, true, status, 0u, &plan) != R1_OK) {
        return;
    }
    if (plan.release_credit) {
        (void)osSemaphoreRelease(phone_credits);
    }
    if (!plan.retry_once) {
        return;
    }
    (void)osDelay(plan.retry_delay_ticks);
    if (osSemaphoreAcquire(phone_credits, R1_EUS_CREDIT_WAIT_TICKS) != osOK) {
        return;
    }
    status = openr1_bae8_transmit(event);
    if (r1_bae8_plan_hvx_result(
            true, true, status, 1u, &plan) == R1_OK &&
        plan.release_credit) {
        (void)osSemaphoreRelease(phone_credits);
    }
}

static void channel1_worker(void *context) {
    (void)context;
    for (;;) {
        r1_tx_event event;
        if (osMessageQueueGet(channel1_queue, &event, NULL, osWaitForever) == osOK) {
            send_channel1(&event);
        }
    }
}

static void runtime_worker(void *context) {
    (void)context;
    for (;;) {
        r1_tx_event event;
        if (osMessageQueueGet(shared_queue, &event, NULL, osWaitForever) == osOK) {
            if (event.channel == 2u) {
                send_eus(&event);
            } else {
                send_channel1(&event);
            }
        }
    }
}

static r1_error enqueue_tx(void *context, bool use_shared_queue,
                           const r1_tx_event *event, uint32_t wait_ticks) {
    (void)context;
    if (event == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const osMessageQueueId_t queue = use_shared_queue
        ? shared_queue : channel1_queue;
    return osMessageQueuePut(queue, event, 0u, wait_ticks) == osOK
        ? R1_OK : R1_ERROR_CAPACITY;
}

static void softdevice_worker(void *context) {
    (void)context;
    platform_startup();
    for (;;) {
        /* Poll before blocking so an event raised during startup is consumed. */
        nrf_sdh_evts_poll();
        (void)osThreadFlagsWait(
            OPENR1_SOFTDEVICE_WAKE_FLAG, osFlagsWaitAny, osWaitForever);
    }
}

void SD_EVT_IRQHandler(void) {
    if (softdevice_thread != NULL) {
        (void)osThreadFlagsSet(softdevice_thread, OPENR1_SOFTDEVICE_WAKE_FLAG);
    }
}

uint32_t openr1_scheduler_initialize(openr1_startup_fn startup) {
    static const osThreadAttr_t channel1_attributes = {
        .name = "channel1_tx",
        .cb_mem = &channel1_control_block,
        .cb_size = sizeof channel1_control_block,
        .stack_mem = channel1_stack,
        .stack_size = sizeof channel1_stack,
    };
    static const osThreadAttr_t runtime_attributes = {
        .name = "eus_tx",
        .cb_mem = &runtime_control_block,
        .cb_size = sizeof runtime_control_block,
        .stack_mem = runtime_stack,
        .stack_size = sizeof runtime_stack,
    };
    static const osThreadAttr_t softdevice_attributes = {
        .name = "BLE",
        .cb_mem = &softdevice_control_block,
        .cb_size = sizeof softdevice_control_block,
        .stack_mem = softdevice_stack,
        .stack_size = sizeof softdevice_stack,
    };
    if (startup == NULL || osKernelInitialize() != osOK) {
        return NRF_ERROR_INVALID_STATE;
    }
    platform_startup = startup;
    channel1_queue = osMessageQueueNew(
        R1_NORMAL_QUEUE_CAPACITY, sizeof(r1_tx_event), NULL);
    shared_queue = osMessageQueueNew(
        R1_EUS_QUEUE_CAPACITY, sizeof(r1_tx_event), NULL);
    glasses_credits = osSemaphoreNew(
        R1_HVN_CREDIT_MAX, R1_HVN_CREDIT_MAX, NULL);
    phone_credits = osSemaphoreNew(
        R1_HVN_CREDIT_MAX, R1_HVN_CREDIT_MAX, NULL);
    if (channel1_queue == NULL || shared_queue == NULL ||
        glasses_credits == NULL || phone_credits == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    r1_runtime_set_enqueue(openr1_platform_runtime(), enqueue_tx, NULL);
    channel1_thread = osThreadNew(
        channel1_worker, NULL, &channel1_attributes);
    runtime_thread = osThreadNew(runtime_worker, NULL, &runtime_attributes);
    softdevice_thread = osThreadNew(
        softdevice_worker, NULL, &softdevice_attributes);
    if (channel1_thread == NULL || runtime_thread == NULL ||
        softdevice_thread == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    return openr1_watchdog_initialize();
}

void openr1_scheduler_start(void) {
    if (osKernelStart() != osOK) {
        for (;;) {
            __WFE();
        }
    }
    for (;;) {
        __WFE();
    }
}

static osSemaphoreId_t credits_for_role(r1_peer_role role) {
    if (role == R1_ROLE_GLASSES) {
        return glasses_credits;
    }
    return role == R1_ROLE_PHONE ? phone_credits : NULL;
}

static void release_credits(osSemaphoreId_t credits, uint8_t completed) {
    if (credits == NULL) {
        return;
    }
    for (uint8_t index = 0u; index < completed; ++index) {
        if (osSemaphoreRelease(credits) != osOK) {
            break;
        }
    }
}

void openr1_scheduler_complete_credits(r1_peer_role role, uint8_t completed) {
    const osSemaphoreId_t credits = credits_for_role(role);
    if (credits != NULL) {
        release_credits(credits, completed);
    } else {
        release_credits(glasses_credits, completed);
        release_credits(phone_credits, completed);
    }
}

static void refill_credits(osSemaphoreId_t credits) {
    if (credits == NULL) {
        return;
    }
    while (osSemaphoreAcquire(credits, 0u) == osOK) {
    }
    release_credits(credits, R1_HVN_CREDIT_MAX);
}

void openr1_scheduler_reset_credits(r1_peer_role role) {
    const osSemaphoreId_t credits = credits_for_role(role);
    if (credits != NULL) {
        refill_credits(credits);
    } else {
        refill_credits(glasses_credits);
        refill_credits(phone_credits);
    }
}

void vApplicationGetIdleTaskMemory(
    StaticTask_t **control_block, StackType_t **stack, uint32_t *words) {
    *control_block = &idle_control_block;
    *stack = idle_stack;
    *words = configMINIMAL_STACK_SIZE;
}

void vApplicationGetTimerTaskMemory(
    StaticTask_t **control_block, StackType_t **stack, uint32_t *words) {
    *control_block = &timer_control_block;
    *stack = timer_stack;
    *words = configTIMER_TASK_STACK_DEPTH;
}

void vApplicationStackOverflowHook(TaskHandle_t task, char *task_name) {
    (void)task;
    (void)SEGGER_RTT_WriteString(0u, "[RING]Stack overflow in task: ");
    (void)SEGGER_RTT_WriteString(
        0u, task_name != NULL ? task_name : "<unknown>");
    (void)SEGGER_RTT_WriteString(0u, "\n");
    for (;;) {
        __WFE();
    }
}

bool openr1_scheduler_task_stack(
    void *task, uint32_t **start, uint32_t *words) {
    if (start == NULL || words == NULL) {
        return false;
    }
    const TaskHandle_t handle = (TaskHandle_t)task;
    if (handle == (TaskHandle_t)channel1_thread) {
        *start = (uint32_t *)channel1_stack;
        *words = configMINIMAL_STACK_SIZE;
        return true;
    }
    if (handle == (TaskHandle_t)runtime_thread) {
        *start = (uint32_t *)runtime_stack;
        *words = configMINIMAL_STACK_SIZE;
        return true;
    }
    if (handle == (TaskHandle_t)softdevice_thread) {
        *start = (uint32_t *)softdevice_stack;
        *words = configMINIMAL_STACK_SIZE;
        return true;
    }
    if (handle == xTaskGetIdleTaskHandle()) {
        *start = (uint32_t *)idle_stack;
        *words = configMINIMAL_STACK_SIZE;
        return true;
    }
    if (handle == xTimerGetTimerDaemonTaskHandle()) {
        *start = (uint32_t *)timer_stack;
        *words = configTIMER_TASK_STACK_DEPTH;
        return true;
    }
    *start = NULL;
    *words = 0u;
    return false;
}

bool openr1_scheduler_current_stack(uint32_t **start, uint32_t *words) {
    return openr1_scheduler_task_stack(
        (void *)xTaskGetCurrentTaskHandle(), start, words);
}
