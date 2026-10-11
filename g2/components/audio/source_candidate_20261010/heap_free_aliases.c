/* Both audio callers branch to Apollo MAIN vPortFree at 0x456210. */
#include "../cmsis_memory_pool_offline/heap.c"

__asm__(".global audio_aux_free\n.set audio_aux_free, vPortFree\n"
        ".global audio_timer_heap_free\n.set audio_timer_heap_free, vPortFree\n");
