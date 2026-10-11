/* Stock 0x4d3c0a..0x4d3cad: AM RTC BCD calendar read. */
#include <stdint.h>
extern uint32_t g2_gpio_critical_save(void); /* stock 0x473940 */
extern void audio_rtc_latch(void); /* stock 0x4d3b9a, hardware sequence */
static uint32_t bcd(uint32_t value)
{
    uint8_t x=(uint8_t)value;
    return (uint8_t)(((x>>4u)*10u)+(x&15u));
}
static void put32(uint8_t *p,uint32_t value)
{
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8u);
    p[2]=(uint8_t)(value>>16u);p[3]=(uint8_t)(value>>24u);
}
uint32_t audio_rtc_read_calendar(uint8_t out[40])
{
    uint32_t prior=g2_gpio_critical_save();
    audio_rtc_latch();
    uint32_t timereg=*(volatile uint32_t *)(uintptr_t)0x40004820u;
    uint32_t datereg=*(volatile uint32_t *)(uintptr_t)0x40004824u;
    __asm volatile("msr PRIMASK, %0" :: "r"(prior) : "memory");
    uint32_t invalid=datereg>>31u;
    put32(out,invalid);
    if (invalid) return 1u;
    put32(out+24u,bcd((timereg>>24u)&63u));
    put32(out+28u,bcd((timereg>>16u)&127u));
    put32(out+32u,bcd((timereg>>8u)&127u));
    put32(out+36u,bcd(timereg&255u));
    put32(out+8u,(datereg>>28u)&1u);
    put32(out+4u,bcd((datereg>>24u)&7u));
    put32(out+12u,bcd((datereg>>16u)&255u));
    put32(out+16u,bcd((datereg>>8u)&31u));
    put32(out+20u,bcd(datereg&63u));
    return 0u;
}
