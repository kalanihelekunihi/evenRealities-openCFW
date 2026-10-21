/* Apollo main 0x4558a4: FreeRTOS xTaskGetSchedulerState. */
#include <stdint.h>

extern volatile uint32_t audio_os_scheduler_running_20074a3c;
extern volatile uint32_t audio_os_scheduler_suspended_20074a58;

uint32_t audio_os_scheduler_state_4558a4(void) {
    if (audio_os_scheduler_running_20074a3c == 0u) return 1u;
    if (audio_os_scheduler_suspended_20074a58 == 0u) return 2u;
    return 0u;
}
