#include <stdint.h>

#include "FreeRTOS.h"
#include "app_timer.h"
#include "task.h"

/* Nordic's FreeRTOS app_timer backend omits these read-only legacy helpers. */
uint32_t app_timer_cnt_get(void) {
    return ((uint32_t)xTaskGetTickCount()) & APP_TIMER_MAX_CNT_VAL;
}

uint32_t app_timer_cnt_diff_compute(uint32_t ticks_to, uint32_t ticks_from) {
    return (ticks_to - ticks_from) & APP_TIMER_MAX_CNT_VAL;
}
