/* Apollo S200 xTaskGetSchedulerState at 0x4558a4. */
#include <stdint.h>

uint32_t display_driver_uled_scheduler_state_4558a4(void) {
    if (*(volatile const uint32_t *)(uintptr_t)0x20074a3cu == 0u) return 1u;
    if (*(volatile const uint32_t *)(uintptr_t)0x20074a58u == 0u) return 2u;
    return 0u;
}
