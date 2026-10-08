#include <stdint.h>
/* Functional offline reconstructions of runtime ITCM helpers. Not cycle-exact C. */
uint32_t audio_itcm_delay_iterations(uint32_t iterations) {
    /* Stock do/while contract requires positive iterations; zero wraps. */
    volatile uint32_t remaining=iterations;
    do { remaining--; } while(remaining);
    return remaining;
}
const uint32_t *audio_itcm_read_words(const volatile uint32_t *source,volatile uint32_t *destination,uint32_t words) {
    /* Positive word count and mapped nonoverlapping buffers are test preconditions. */
    do { *destination++=*source++; } while(--words);
    return (const uint32_t *)source;
}
extern uint32_t actual_itcm_delay(uint32_t iterations);
void audio_delay_us_selected(uint32_t us) {
    /* Selected tested range0..100 us. Unsigned fixed-conversion saturation at
       extreme input is outside this C reconstruction's validated domain. */
    uint32_t iterations=(uint32_t)((float)us*32.0f),adjust=15;
    if(((*(volatile uint32_t *)(uintptr_t)0x40021000>>3)&3u)==2) {
        iterations=(uint32_t)((float)iterations*250.0f/96.0f);adjust=24;
    }
    if(iterations>adjust) (void)actual_itcm_delay(iterations-adjust);
}
