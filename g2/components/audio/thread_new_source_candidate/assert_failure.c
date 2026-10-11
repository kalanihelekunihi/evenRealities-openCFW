/* Shared source form of the stock FreeRTOS assertion fault prefix. */
#include <stdint.h>
extern uint32_t audio_mask_save(void); /* stock 0x5fa0a4 */
void g2_thread_assert_failure(void) __attribute__((noreturn));
void g2_thread_assert_failure(void) {
    (void)audio_mask_save();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    for(;;) __asm__ volatile("nop");
}
void g2_event_wait_assert(void) __attribute__((alias("g2_thread_assert_failure")));
void g2_event_place_assert(void) __attribute__((alias("g2_thread_assert_failure")));
