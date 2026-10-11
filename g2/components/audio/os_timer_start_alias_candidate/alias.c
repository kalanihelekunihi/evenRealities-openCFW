#include <stdint.h>

/* Stock 0x00449498 and selected audio_timer_start are the same CMSIS
 * two-argument entry: IRQ rejection, timer/tick validation, command 4
 * publication, and status mapping. This name serves native callers. */
extern int32_t audio_timer_start(void *timer, uint32_t ticks);

int32_t osTimerStart(void *timer, uint32_t ticks) {
    return audio_timer_start(timer, ticks);
}
