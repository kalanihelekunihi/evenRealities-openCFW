#include <stdint.h>

/* Original 0x0800c0a0..0x0800c0b2 requests PendSV in SCB ICSR. */
/* Stock 0x0800C0A0 (case_yield_request) */
uint32_t case_yield_request(void)
{
    const uint32_t request = 0x10000000u;
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u = request;
    __asm__ volatile("dsb sy\n\tisb sy" : : : "memory");
    return request;
}
