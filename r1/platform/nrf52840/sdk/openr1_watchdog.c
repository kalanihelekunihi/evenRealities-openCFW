#include "openr1_watchdog.h"

#include "cmsis_os2.h"
#include "FreeRTOS.h"
#include "nrfx_wdt.h"
#include "task.h"

#define OPENR1_WATCHDOG_RELOAD_MILLISECONDS 10000u
#define OPENR1_WATCHDOG_INTERRUPT_PRIORITY 6u
#define OPENR1_WATCHDOG_FEED_TICKS 1024u

static nrfx_wdt_channel_id watchdog_channel;
static StaticTask_t watchdog_control_block;
static StackType_t watchdog_stack[configMINIMAL_STACK_SIZE];

static void watchdog_timeout(void) {
    /* Match the recovered no-op timeout handler; hardware reset follows. */
}

static void watchdog_worker(void *context) {
    (void)context;
    for (;;) {
        nrfx_wdt_channel_feed(watchdog_channel);
        (void)osDelay(OPENR1_WATCHDOG_FEED_TICKS);
    }
}

ret_code_t openr1_watchdog_initialize(void) {
    static const nrfx_wdt_config_t configuration = {
        .behaviour = NRF_WDT_BEHAVIOUR_RUN_SLEEP,
        .reload_value = OPENR1_WATCHDOG_RELOAD_MILLISECONDS,
        .interrupt_priority = OPENR1_WATCHDOG_INTERRUPT_PRIORITY,
    };
    static const osThreadAttr_t attributes = {
        .name = "watchdog",
        .cb_mem = &watchdog_control_block,
        .cb_size = sizeof watchdog_control_block,
        .stack_mem = watchdog_stack,
        .stack_size = sizeof watchdog_stack,
        .priority = osPriorityLow,
    };

    ret_code_t error = nrfx_wdt_init(&configuration, watchdog_timeout);
    if (error != NRF_SUCCESS) {
        return error;
    }
    error = nrfx_wdt_channel_alloc(&watchdog_channel);
    if (error != NRF_SUCCESS) {
        return error;
    }
    if (osThreadNew(watchdog_worker, NULL, &attributes) == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    nrfx_wdt_enable();
    return NRF_SUCCESS;
}
