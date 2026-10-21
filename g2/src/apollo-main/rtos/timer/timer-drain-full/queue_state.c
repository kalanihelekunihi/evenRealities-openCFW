/* Apollo MAIN timer command queue handle at 0x20074ab0. Both historical
 * names address the same zero-initialized RAM word; final placement remains
 * a linker contract. */
#include <stdint.h>

_Static_assert(sizeof(void *) == sizeof(uintptr_t), "queue handle width");
void *g2_audio_timer_command_queue;
extern volatile uintptr_t audio_uart_ring_persist_queue_handle_20074ab0
    __attribute__((alias("g2_audio_timer_command_queue")));
