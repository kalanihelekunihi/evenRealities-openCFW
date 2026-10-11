#include <stdint.h>

/* Stock 0x4d3610 writes the timer-daemon TCB, stack and depth to three
 * caller-provided output cells. The original body has no null checks. */
void audio_daemon_get_static_memory(void **tcb, void **stack, uint32_t *depth) {
    *tcb = (void *)(uintptr_t)0x20071ea0u;
    *stack = (void *)(uintptr_t)0x2003fa98u;
    *depth = 4096u;
}
