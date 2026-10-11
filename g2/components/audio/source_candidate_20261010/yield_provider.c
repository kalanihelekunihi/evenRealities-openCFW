#include <stdint.h>

/* Stock 0x4420bc sets PENDSVSET in ICSR then orders the request.
 * The same bounded source contract exists in foundation/freertos_resume. */
void audio_yield(void) {
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u = 0x10000000u;
    __asm__ volatile("dsb\n\tisb" ::: "memory");
}
void stock_port_yield(void) __attribute__((alias("audio_yield")));
void stock_yield(void) __attribute__((alias("audio_yield")));
void opencfw_resume_yield_request(void) __attribute__((alias("audio_yield")));
