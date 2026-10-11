#include <stdint.h>

extern uint32_t audio_cmsis_irq_context(void);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern uint32_t audio_mask_save(void);
extern int32_t audio_aux_command(void *, int32_t, uint32_t, void *, uint32_t);

uint32_t audio_timer_is_active(void *timer) {
    if (!timer) {
        (void)audio_mask_save();
        *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0;
        for (;;) { }
    }
    stock_enter_critical();
    uint32_t active = (*(volatile uint8_t *)((uintptr_t)timer + 0x28u)) & 1u;
    stock_exit_critical();
    return active;
}

int32_t audio_timer_stop(void *timer) {
    if (audio_cmsis_irq_context()) return -6;
    if (!timer) return -4;
    if (!audio_timer_is_active(timer)) return -3;
    return audio_aux_command(timer, 3, 0, 0, 0) == 1 ? 0 : -1;
}
