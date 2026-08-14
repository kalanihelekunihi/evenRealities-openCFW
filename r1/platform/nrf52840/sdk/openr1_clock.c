#include "openr1_clock.h"

#include <string.h>
#include <time.h>

#include "cmsis_os2.h"
#include "FreeRTOS.h"
#include "task.h"

#include "openr1/r1_clock.h"
#include "openr1/r1_runtime.h"

extern r1_runtime *openr1_platform_runtime(void);

#define OPENR1_CLOCK_CADENCE_TICKS 1024u

static r1_clock platform_clock;
static StaticTask_t clock_control_block;
static StackType_t clock_stack[configMINIMAL_STACK_SIZE];
static uint32_t adopted_epoch;
static int16_t adopted_offset_minutes;
static bool adoption_valid;

void openr1_clock_adopt_phone_time(uint32_t epoch_seconds,
                                   int16_t utc_offset_minutes) {
    if (r1_clock_synchronize(&platform_clock, epoch_seconds,
                             utc_offset_minutes,
                             xTaskGetTickCount()) != R1_OK) {
        return;
    }
    adopted_epoch = epoch_seconds;
    adopted_offset_minutes = utc_offset_minutes;
    adoption_valid = true;
}

static void clock_worker(void *context) {
    (void)context;
    r1_runtime *runtime = openr1_platform_runtime();
    for (;;) {
        /* Pick up a direct portable-state time-set within one cadence. */
        const uint32_t state_epoch = runtime->device.unix_seconds;
        const int16_t state_offset =
            (int16_t)runtime->device.timezone_minutes_raw;
        if (state_epoch != 0u &&
            (!adoption_valid || state_epoch != adopted_epoch ||
             state_offset != adopted_offset_minutes)) {
            openr1_clock_adopt_phone_time(state_epoch, state_offset);
        }
        (void)osDelay(OPENR1_CLOCK_CADENCE_TICKS);
    }
}

ret_code_t openr1_clock_initialize(void) {
    static const osThreadAttr_t attributes = {
        .name = "clock",
        .cb_mem = &clock_control_block,
        .cb_size = sizeof clock_control_block,
        .stack_mem = clock_stack,
        .stack_size = sizeof clock_stack,
        .priority = osPriorityLow,
    };

    r1_clock_initialize(&platform_clock, 1024u);
    adopted_epoch = 0u;
    adopted_offset_minutes = 0;
    adoption_valid = false;
    if (osThreadNew(clock_worker, NULL, &attributes) == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    return NRF_SUCCESS;
}

bool openr1_clock_epoch(uint32_t *epoch_seconds) {
    return r1_clock_now(&platform_clock, xTaskGetTickCount(), epoch_seconds);
}

bool openr1_clock_local_tm(struct tm *out) {
    if (out == NULL) {
        return false;
    }
    uint32_t local_seconds = 0u;
    if (!r1_clock_local_now(&platform_clock, xTaskGetTickCount(),
                            &local_seconds)) {
        return false;
    }
    const time_t moment = (time_t)local_seconds;
    return gmtime_r(&moment, out) != NULL;
}

/* Retain the query API surface the same way the other platform seams are
 * retained: a function-pointer table in a KEEP section, so the linker cannot
 * garbage-collect the query path that health storage will consume. */
typedef struct {
    bool (*epoch)(uint32_t *);
    bool (*local_tm)(struct tm *);
} openr1_clock_api;

__attribute__((used, section(".openr1_clock_api")))
static const openr1_clock_api retained_clock_api = {
    openr1_clock_epoch,
    openr1_clock_local_tm,
};
