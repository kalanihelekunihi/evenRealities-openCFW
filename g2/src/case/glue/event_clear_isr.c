#include <stdint.h>

extern void vEventGroupClearBitsCallback(void *event_group, uint32_t bits);
/* The selected CASE producer uses four 32-bit ARM AAPCS words. */
extern int32_t xTimerPendFunctionCallFromISR(
    uint32_t callback, uint32_t argument1, uint32_t argument2,
    int32_t *higher_priority_task_woken);

/* Stock 0x0800c478..0x0800c48c, including callback literal. */
uint32_t xEventGroupClearBitsFromISR(void *event_group, uint32_t bits)
{
    return xTimerPendFunctionCallFromISR(
        (uint32_t)(uintptr_t)vEventGroupClearBitsCallback,
        (uint32_t)(uintptr_t)event_group, bits, (int32_t *)0);
}
