/* Reset sequencing from the pinned Nordic nRF52840 GCC startup source.
 * The vector table supplies the initial stack pointer before this C entry.
 * Aligned linker ranges include initialized registration data before BSS. */
#include <stdint.h>
extern uint32_t __etext[], __data_start__[], __bss_start__[];
extern void SystemInit(void);
extern __attribute__((noreturn)) void _start(void);
_Static_assert(sizeof(uintptr_t) == 4, "nRF52840 address width");

__attribute__((noreturn)) void Reset_Handler(void)
{
    uintptr_t begin = (uintptr_t)__data_start__;
    uintptr_t end = (uintptr_t)__bss_start__;
    if (end > begin) {
        uintptr_t remaining = end - begin;
        do {
            remaining -= sizeof(uint32_t);
            *(volatile uint32_t *)(begin + remaining) =
                *(const volatile uint32_t *)((uintptr_t)__etext + remaining);
        } while (remaining);
    }
    SystemInit();
    _start();
}
