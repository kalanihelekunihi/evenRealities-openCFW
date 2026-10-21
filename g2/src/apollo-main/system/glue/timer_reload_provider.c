#include <stdint.h>

/* Apollo MAIN 0x47e812. Child and callback retain their original ABIs. */
extern uint32_t audio_timer_reload_insert(uint32_t *timer, uint32_t next,
                                          uint32_t now, uint32_t expiry);

void stock_timer_reload(uint32_t *timer, uint32_t expiry, uint32_t now) {
    for (;;) {
        uint32_t next = timer[6] + expiry;
        if (audio_timer_reload_insert(timer, next, now, expiry) == 0)
            return;
        expiry += timer[6];
        ((void (*)(uint32_t *))(uintptr_t)timer[8])(timer);
    }
}
