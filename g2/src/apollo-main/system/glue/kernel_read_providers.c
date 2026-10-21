#include <stdint.h>

/* Original xTaskGetTickCount at 0x454efe consists of an LDR literal,
 * LDR [r0], BX LR. The literal at 0x4557ac is 0x20074a34. */
uint32_t audio_tick(void) {
    return *(volatile const uint32_t *)(uintptr_t)0x20074a34u;
}
uint32_t audio_timer_wrap_get_tick(void) __attribute__((alias("audio_tick")));
uint32_t stock_tick_count(void) __attribute__((alias("audio_tick")));

/* Original xTaskGetCurrentTaskHandle at 0x45589c has the same three
 * instructions; its literal at 0x45605c is 0x20074a20. */
void *receiver_current_task(void) {
    return *(void *volatile const *)(uintptr_t)0x20074a20u;
}
