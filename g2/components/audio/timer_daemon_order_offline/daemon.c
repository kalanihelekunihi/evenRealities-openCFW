#include "daemon.h"
#include "../timer_commands_offline/timer.h"
extern void stock_timer_drain_commands(void);
extern void stock_scheduler_suspend(void);
extern int32_t stock_scheduler_resume(void);
extern uint32_t stock_tick_count(void);
extern void stock_timer_switch_lists(void);
extern uint32_t stock_list_remove(audio_timer_list_item *item);
extern void stock_timer_reload(audio_timer_prefix *timer,uint32_t expiry,uint32_t now);
extern void stock_queue_restricted_wait(void *queue,uint32_t ticks,uint32_t indefinite);
extern void stock_yield(void);
uint32_t audio_timer_next_expiry(uint32_t *list_empty) {
    uint32_t *list = *(uint32_t **)0x20074aa8u;
    *list_empty = list[0] == 0;
    return *list_empty ? 0 : *(uint32_t *)list[3];
}
uint32_t audio_timer_sample_time(uint32_t *lists_switched) {
    uint32_t now = stock_tick_count();
    volatile uint32_t *last = (volatile uint32_t *)0x20074ab8u;
    if (now < *last) {
        stock_timer_switch_lists();
        *lists_switched = 1;
    } else {
        *lists_switched = 0;
    }
    *last = now;
    return now;
}
void audio_timer_expired(uint32_t expiry,uint32_t now) {
    uint32_t *list = *(uint32_t **)0x20074aa8u;
    audio_timer_list_item *head = (audio_timer_list_item *)list[3];
    audio_timer_prefix *timer = (audio_timer_prefix *)head->owner;
    (void)stock_list_remove(&timer->item);
    if (timer->status & AUDIO_TIMER_AUTORELOAD)
        stock_timer_reload(timer,expiry,now);
    else
        timer->status &= (uint8_t)~AUDIO_TIMER_ACTIVE;
    ((void (*)(audio_timer_prefix *))timer->callback)(timer);
}
void audio_timer_process_or_block(uint32_t expiry,uint32_t empty) {
    uint32_t switched;
    stock_scheduler_suspend();
    uint32_t now = audio_timer_sample_time(&switched);
    if (switched) {
        (void)stock_scheduler_resume();
    } else if (!empty && now >= expiry) {
        (void)stock_scheduler_resume();
        audio_timer_expired(expiry,now);
    } else {
        if (empty) {
            uint32_t *overflow = *(uint32_t **)0x20074aacu;
            empty = overflow[0] == 0;
        }
        stock_queue_restricted_wait(*(void **)0x20074ab0u,expiry-now,empty);
        if (!stock_scheduler_resume()) stock_yield();
    }
}
void audio_timer_daemon(void *unused) {
    (void)unused;
    for (;;) {
        uint32_t empty;
        uint32_t expiry = audio_timer_next_expiry(&empty);
        audio_timer_process_or_block(expiry,empty);
        stock_timer_drain_commands();
    }
}
