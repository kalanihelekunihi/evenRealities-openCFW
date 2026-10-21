/* Apollo MAIN 0x47e97a..0x47ea8f, FreeRTOS timer daemon command drain.
 * Selected children correspond to the original queue/list/time/insert/free
 * entries. Product queue handle is an explicit RAM contract. */
#include <stdint.h>
#include "../timer-commands/timer.h"

extern void *g2_audio_timer_command_queue; /* 0x20074ab0 */
extern int32_t audio_timer_queue_receive(void *,void *,uint32_t);
extern uint32_t audio_timer_list_remove(void *);
extern uint32_t audio_timer_sample_time(uint32_t *);
extern uint32_t audio_timer_reload_insert(uint32_t *,uint32_t,uint32_t,uint32_t);
extern void stock_timer_reload(uint32_t *,uint32_t,uint32_t);
extern void audio_timer_heap_free(void *);
extern void offline_assert(void) __attribute__((noreturn));

void audio_daemon_drain_commands(void)
{
    audio_timer_message message;
    while (audio_timer_queue_receive(g2_audio_timer_command_queue,&message,0u)) {
        if (message.command < 0) {
            void (*callback)(void *,uint32_t) =
                (void (*)(void *,uint32_t))(uintptr_t)message.value;
            callback(message.timer,message.union_padding);
            continue;
        }
        audio_timer_prefix *timer=message.timer;
        if (timer->item.container != 0u)
            (void)audio_timer_list_remove(&timer->item);
        uint32_t switched;
        uint32_t now=audio_timer_sample_time(&switched);
        (void)switched;
        switch (message.command) {
        case 1: case 2: case 6: case 7:
            timer->status |= AUDIO_TIMER_ACTIVE;
            if (audio_timer_reload_insert((uint32_t *)(void *)timer,
                    message.value+timer->period,now,message.value)) {
                if (timer->status&AUDIO_TIMER_AUTORELOAD)
                    stock_timer_reload((uint32_t *)(void *)timer,
                                       message.value+timer->period,now);
                else
                    timer->status &= (uint8_t)~AUDIO_TIMER_ACTIVE;
                ((void (*)(audio_timer_prefix *))(uintptr_t)timer->callback)(timer);
            }
            break;
        case 3: case 8:
            timer->status &= (uint8_t)~AUDIO_TIMER_ACTIVE;
            break;
        case 4: case 9:
            timer->status |= AUDIO_TIMER_ACTIVE;
            timer->period=message.value;
            if (timer->period == 0u) offline_assert();
            (void)audio_timer_reload_insert((uint32_t *)(void *)timer,
                       now+timer->period,now,now);
            break;
        case 5:
            if (!(timer->status&AUDIO_TIMER_STATIC))
                audio_timer_heap_free(timer);
            else
                timer->status &= (uint8_t)~AUDIO_TIMER_ACTIVE;
            break;
        default:
            break;
        }
    }
}
void stock_timer_drain_commands(void)
    __attribute__((alias("audio_daemon_drain_commands")));
