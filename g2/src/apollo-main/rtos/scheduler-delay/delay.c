/* Experimental Apollo CMSIS osDelay / FreeRTOS vTaskDelay composition.
 * Source: retained CMSIS-RTOS2 FreeRTOS adapter osDelay and FreeRTOS tasks.c,
 * with Apollo addresses and selected lower aliases from source evidence.
 * This remains outside the admitted audio archive pending joint scheduler oracle. */
#include <stdint.h>
extern uint32_t audio_irq_context(void);
extern void audio_suspend(void);
extern void audio_add_current_to_delayed(uint32_t ticks, uint32_t can_block_indefinitely);
extern int32_t audio_resume(void);
extern void audio_yield(void);
/* Fatal assertion contract on a suspended scheduler. Must not return. */
extern void audio_delay_scheduler_assert(void) __attribute__((noreturn));

static void vTaskDelay_candidate(uint32_t ticks) {
    int32_t already_yielded = 0;
    if (ticks != 0u) {
        if (*(volatile uint32_t *)(uintptr_t)0x20074a58u != 0u)
            audio_delay_scheduler_assert();
        audio_suspend();
        audio_add_current_to_delayed(ticks, 0u);
        already_yielded = audio_resume();
    }
    if (already_yielded == 0) audio_yield();
}

uint32_t audio_delay(uint32_t ticks) {
    if (audio_irq_context() != 0u) return 0xfffffffau;
    if (ticks != 0u) vTaskDelay_candidate(ticks);
    return 0u;
}
uint32_t codec_delay(uint32_t) __attribute__((alias("audio_delay")));
uint32_t codec_delay_tick(uint32_t) __attribute__((alias("audio_delay")));
