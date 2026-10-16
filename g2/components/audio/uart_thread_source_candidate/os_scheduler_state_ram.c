/* Apollo main xTaskGetSchedulerState RAM words at 0x20074a3c/0x20074a58. */
#include <stdint.h>

volatile uint32_t audio_os_scheduler_running_20074a3c
    __attribute__((section(".bss.opencfw.os.scheduler.running"), aligned(4), used));
volatile uint32_t audio_os_scheduler_suspended_20074a58
    __attribute__((section(".bss.opencfw.os.scheduler.suspended"), aligned(4), used));

_Static_assert(sizeof(audio_os_scheduler_running_20074a3c) == 4u, "running cell");
_Static_assert(sizeof(audio_os_scheduler_suspended_20074a58) == 4u, "suspended cell");
