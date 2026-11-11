/* Distinct native input queues, direct ring descriptor, and failure text. */
#include <stdint.h>

/* audio_uart_input_mutex: same stock cell as another object; now an alias there (see sim-test-report Fix 31). */
/* audio_uart_input_queue: same stock cell as another object; now an alias there (see sim-test-report Fix 31). */
/* audio_uart_sync_schedule_queue: same stock cell as another object; now an alias there (see sim-test-report Fix 31). */
/* audio_uart_input_event_flags: same stock cell as another object; now an alias there (see sim-test-report Fix 31). */
uint32_t g2_display_ring[5] __attribute__((section(".g2_ram_20073b60")));
const char audio_uart_input_queue_failure_context[] =
    "input: message queue send failed";
