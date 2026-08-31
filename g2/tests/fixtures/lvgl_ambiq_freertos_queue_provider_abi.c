/* SPDX-License-Identifier: MIT */
#include "../../third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_freertos_queue_provider.h"

/* Duplicate declarations must be C-type compatible with the public ABI. */
#include "FreeRTOS.h"
#include "queue.h"

_Static_assert(sizeof(BaseType_t) == sizeof(open_cfw_lvgl_freertos_base_type),
               "BaseType_t width mismatch");
_Static_assert(sizeof(UBaseType_t) == sizeof(open_cfw_lvgl_freertos_ubase_type),
               "UBaseType_t width mismatch");
_Static_assert(sizeof(TickType_t) == sizeof(open_cfw_lvgl_freertos_tick_type),
               "TickType_t width mismatch");
_Static_assert(sizeof(QueueHandle_t) == sizeof(open_cfw_lvgl_freertos_queue_handle),
               "QueueHandle_t width mismatch");

int open_cfw_lvgl_freertos_queue_provider_abi_probe(void)
{
    return 0;
}
