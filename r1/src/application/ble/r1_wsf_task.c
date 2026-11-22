/* FreeRTOS owner of Cordio's bare-metal WSF event and timer dispatch.
 * The controller's RTC1 ISR stays independent of this task. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>

#include "FreeRTOS.h"
#include "task.h"
#include "r1_wsf_task.h"
#include "r1_flash_cordio.h"

extern void WsfTimerSleepUpdate(void);
extern void wsfOsDispatcher(void);
extern void r1_cordio_hardware_shutdown(void);

/* BLE IO is priority 52. WSF must finish an ATT callback and arm Cordio's
 * pending-response bit before that worker consumes an authorization event. */
enum { R1_WSF_STACK_WORDS = 512, R1_WSF_TASK_PRIORITY = 54 };
_Static_assert(R1_WSF_TASK_PRIORITY < configMAX_PRIORITIES,
               "WSF priority must fit the R1 FreeRTOS profile");

/* This storage remains in upper application RAM; the link script places only
 * this object's text/rodata in the recovered lower Cordio flash region. */
static StaticTask_t r1_wsf_tcb;
static StackType_t r1_wsf_stack[R1_WSF_STACK_WORDS];
static TaskHandle_t r1_wsf_handle;
static volatile bool r1_wsf_stop_requested;

static void r1_wsf_dispatch_task(void *argument)
{
    (void)argument;
    for (;;) {
        WsfTimerSleepUpdate();
        wsfOsDispatcher();
        r1_cordio_flash_service();
        if (r1_wsf_stop_requested) {
            r1_cordio_hardware_shutdown();
            vTaskSuspend(NULL);
        }
        /* WSF's bare-metal WsfTimerSleep enters CPU sleep and cannot own the
         * R1 scheduler. A single RTOS tick bounds event dispatch latency. */
        vTaskDelay(1);
    }
}

void r1_cordio_wsf_task_stop_request(void)
{
    r1_wsf_stop_requested = true;
}

bool r1_cordio_wsf_task_start(void)
{
    if (r1_wsf_handle != 0) {
        return true;
    }
    r1_wsf_handle = xTaskCreateStatic(r1_wsf_dispatch_task, "cordio",
                                     R1_WSF_STACK_WORDS, 0,
                                     R1_WSF_TASK_PRIORITY,
                                     r1_wsf_stack, &r1_wsf_tcb);
    return r1_wsf_handle != 0;
}

bool r1_cordio_wsf_wait_until(bool (*ready)(void), uint32_t max_ticks)
{
    if (ready == 0 || r1_wsf_handle == 0) {
        return false;
    }
    for (uint32_t waited = 0; waited < max_ticks; ++waited) {
        if (ready()) {
            return true;
        }
        vTaskDelay(1);
    }
    return ready();
}
#endif
