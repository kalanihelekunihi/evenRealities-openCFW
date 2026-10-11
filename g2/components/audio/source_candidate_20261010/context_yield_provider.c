#include <stdint.h>

/* IRQ_Context at 0x44900e: source semantics from the previously validated
 * foundation/audio_pcm_consumer reconstruction. Both public audio aliases
 * were linked to Thumb entry 0x44900f in their original-byte receipts. */
static uint32_t scheduler_state(void) {
    if (!*(volatile uint32_t *)(uintptr_t)0x20074a3cu) return 1;
    return *(volatile uint32_t *)(uintptr_t)0x20074a58u ? 0 : 2;
}
uint32_t audio_irq_context(void) {
    uint32_t value;
    __asm__ volatile("mrs %0, ipsr" : "=r"(value));
    if (value) return 1;
    if (scheduler_state() == 1) return 0;
    __asm__ volatile("mrs %0, primask" : "=r"(value));
    if (value) return 1;
    __asm__ volatile("mrs %0, basepri" : "=r"(value));
    return value != 0;
}
uint32_t audio_aux_irq_context(void) __attribute__((alias("audio_irq_context")));

/* Prior source/stock composition binds audio_resume_yield directly to
 * opencfw_resume_yield_request for original 0x4420bc. */
void audio_resume_yield(void) {
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u = 0x10000000u;
    __asm__ volatile("dsb\n\tisb" ::: "memory");
}
