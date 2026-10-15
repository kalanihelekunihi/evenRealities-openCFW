#include <stdint.h>

/* Native WsfTimerExpired 0x52a542, timer queue at 0x200741b0. */
extern uint32_t audio_wsf_timer_list[2];
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
extern void audio_wsf_queue_remove(void **queue, void *element, void *previous);

void *opencfw_wsf_timer_expired(uint32_t ignored)
{
    (void)ignored;
    WsfTaskLock();
    uint8_t *timer = (uint8_t *)(uintptr_t)audio_wsf_timer_list[0];
    if (timer != 0 && *(uint32_t *)(void *)(timer + 4u) == 0u) {
        audio_wsf_queue_remove((void **)audio_wsf_timer_list, timer, 0);
        timer[0x0du] = 0u;
        WsfTaskUnlock();
        return timer;
    }
    WsfTaskUnlock();
    return 0;
}
