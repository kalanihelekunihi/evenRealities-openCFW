/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_LVGL_AMBIQ_FREERTOS_QUEUE_PROVIDER_H
#define OPEN_CFW_LVGL_AMBIQ_FREERTOS_QUEUE_PROVIDER_H

#include <stdint.h>

#if defined(__arm__)
/* Exact ARM_CM55_NTZ/non_secure FreeRTOS port typedefs. */
typedef long open_cfw_lvgl_freertos_base_type;
typedef unsigned long open_cfw_lvgl_freertos_ubase_type;
#else
/* Fixed-width host oracle equivalents; LP64 long is not the target ABI. */
typedef int32_t open_cfw_lvgl_freertos_base_type;
typedef uint32_t open_cfw_lvgl_freertos_ubase_type;
#endif
typedef uint32_t open_cfw_lvgl_freertos_tick_type;

struct QueueDefinition;
typedef struct QueueDefinition *open_cfw_lvgl_freertos_queue_handle;

_Static_assert(sizeof(open_cfw_lvgl_freertos_base_type) == 4U,
               "G2 FreeRTOS BaseType_t ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_freertos_ubase_type) == 4U,
               "G2 FreeRTOS UBaseType_t ABI changed");
_Static_assert(sizeof(open_cfw_lvgl_freertos_tick_type) == 4U,
               "G2 FreeRTOS TickType_t ABI changed");

open_cfw_lvgl_freertos_queue_handle xQueueGenericCreate(
    open_cfw_lvgl_freertos_ubase_type length,
    open_cfw_lvgl_freertos_ubase_type item_size,
    uint8_t queue_type
);

open_cfw_lvgl_freertos_base_type xQueueGiveFromISR(
    open_cfw_lvgl_freertos_queue_handle queue,
    open_cfw_lvgl_freertos_base_type *higher_priority_task_woken
);

open_cfw_lvgl_freertos_base_type xQueueSemaphoreTake(
    open_cfw_lvgl_freertos_queue_handle queue,
    open_cfw_lvgl_freertos_tick_type ticks_to_wait
);

#endif
