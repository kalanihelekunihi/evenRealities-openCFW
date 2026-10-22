#include <stdint.h>

/* Stock 0x0800c380..0x0800c38a; base literal 0x20000128 + 0x30. */
/* Stock 0x0800C380 (case_suspend_scheduler) */
void case_suspend_scheduler(void)
{
    volatile uint32_t *const suspended = (volatile uint32_t *)(uintptr_t)0x20000158u;
    *suspended = *suspended + 1u;
}
