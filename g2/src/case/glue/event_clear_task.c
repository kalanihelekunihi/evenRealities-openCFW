#include <stdint.h>

extern void case_enter_critical(void);
extern void case_exit_critical(void);

/* Original 0x0800c44c..0x0800c476. Invalid inputs enter a nonreturn loop. */
uint32_t xEventGroupClearBits(void *event_group, uint32_t bits)
{
    if (event_group == (void *)0 || (bits & 0xff000000u) != 0u) {
        __asm__ volatile("cpsid i" : : : "memory");
        for (;;) {
            __asm__ volatile("nop" : : : "memory");
        }
    }
    case_enter_critical();
    volatile uint32_t *const group_bits = (volatile uint32_t *)event_group;
    const uint32_t before = *group_bits;
    *group_bits = before & ~bits;
    case_exit_critical();
    return before;
}
