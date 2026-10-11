/* ABI adapters to pinned FreeRTOS V10.5.1 event-group C bodies.
 * See g2/components/foundation/freertos_event_group/event_groups_subset.c. */
#include "../../foundation/freertos_event_group/event_group.h"

uint32_t g2_log_event_set_task(uint32_t handle,uint32_t bits) {
    return xEventGroupSetBits((EventGroupHandle_t)(uintptr_t)handle,bits);
}

uint32_t g2_log_event_set_isr(uint32_t handle,uint32_t bits,uint32_t *woken) {
    return (uint32_t)xEventGroupSetBitsFromISR(
        (EventGroupHandle_t)(uintptr_t)handle,bits,(BaseType_t *)woken);
}
