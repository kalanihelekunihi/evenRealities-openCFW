#include <stdint.h>

extern uint32_t audio_cmsis_irq_context(void);
extern int32_t audio_aux_command(void *, int32_t, uint32_t, void *, uint32_t);

int32_t audio_timer_start(void *timer, uint32_t ticks) {
    if (audio_cmsis_irq_context()) return -6;
    if (!timer || !ticks) return -4;
    return audio_aux_command(timer, 4, ticks, 0, 0) == 1 ? 0 : -3;
}
