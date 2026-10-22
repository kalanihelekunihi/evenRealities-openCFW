#include <stdint.h>

/* Original 0x08004eac: separate HAL tick word at RAM 0x20000120. */
/* Stock 0x08004EAC (case_tick_word2) */
uint32_t case_tick_word2(void)
{
    return *(volatile uint32_t *)(uintptr_t)0x20000120u;
}
