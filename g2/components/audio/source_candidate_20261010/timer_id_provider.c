/* Apollo MAIN 0x47EB26: CMSIS timer ID read under the kernel critical pair. */
#include <stdint.h>
#include "../timer_commands_offline/timer.h"

extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern uint32_t audio_port_mask_set(void);

uint32_t audio_aux_get_id(audio_timer_prefix *timer) {
    if (!timer) {
        (void)audio_port_mask_set();
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0;
        for (;;) __asm__ volatile("b ." ::: "memory");
    }
    stock_enter_critical();
    uint32_t id = timer->id;
    stock_exit_critical();
    return id;
}
