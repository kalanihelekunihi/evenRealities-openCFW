/* Stock 0x4d3b9a..0x4d3c09: RTC capture transaction via MMIO. */
#include <stdint.h>
extern void audio_rtc_delay(uint32_t); /* stock 0x4807a0 */
void audio_rtc_latch(void)
{
    volatile uint32_t *const control=(volatile uint32_t *)(uintptr_t)0x400083c0u;
    volatile uint32_t *const mode=(volatile uint32_t *)(uintptr_t)0x4000400cu;
    volatile uint32_t *const clear0=(volatile uint32_t *)(uintptr_t)0x400083c8u;
    volatile uint32_t *const clear1=(volatile uint32_t *)(uintptr_t)0x400083ccu;
    volatile uint32_t *const clock=(volatile uint32_t *)(uintptr_t)0x40008010u;
    volatile uint32_t *const counter=(volatile uint32_t *)(uintptr_t)0x400083c4u;
    *control &= ~1u;
    uint32_t setting=((*mode&128u)?6u:10u);
    *control=((setting<<8u)&0x1ff00u)|16u;
    *clear0=0xffffffffu;
    *clear1=0xffffffffu;
    *clock |= 0x4000u;
    *control |= 2u;
    *control &= ~2u;
    *control |= 1u;
    for (;;) {
        uint32_t first=*counter;
        uint32_t second=*counter;
        if(first!=second) break;
    }
    *control &= ~1u;
    audio_rtc_delay(10u);
}
