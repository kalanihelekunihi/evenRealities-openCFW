/* FreeRTOS event-list item reset, stock 0x455aca. */
#include <stdint.h>
uint32_t g2_event_reset_item_value(void) {
    uint8_t *tcb=*(uint8_t *volatile *)(uintptr_t)0x20074a20u;
    uint32_t prior=*(uint32_t *)(void *)(tcb+0x18u);
    uint32_t priority=*(uint32_t *)(void *)(tcb+0x2cu);
    *(uint32_t *)(void *)(tcb+0x18u)=56u-priority;
    return prior;
}
