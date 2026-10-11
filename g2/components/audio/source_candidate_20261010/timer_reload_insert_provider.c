#include <stdint.h>

/* Apollo MAIN 0x47e93c. List insertion keeps its source-backed child ABI. */
extern void audio_public_list_insert(void *list, void *item);

uint32_t audio_timer_reload_insert(uint32_t *timer, uint32_t next,
                                   uint32_t now, uint32_t expiry) {
    timer[1] = next;
    timer[4] = (uint32_t)(uintptr_t)timer;
    if (now >= next) {
        if (now - expiry >= timer[6])
            return 1;
        audio_public_list_insert(*(void *volatile *)(uintptr_t)0x20074AACu, timer + 1);
    } else {
        if (now < expiry && next >= expiry)
            return 1;
        audio_public_list_insert(*(void *volatile *)(uintptr_t)0x20074AA8u, timer + 1);
    }
    return 0;
}
