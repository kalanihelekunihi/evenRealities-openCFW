/* C runtime handoff for the Nordic-derived C reset handler. That handler
 * copies initialized data and calls SystemInit before entering this function.
 * The current C-only bootloader has no preinit/init/fini array entries. */
#include <stdint.h>
extern uint32_t __bss_start__[],__bss_end__[];
extern int main(void);
__attribute__((noreturn)) void _start(void)
{
    for (uintptr_t cursor=(uintptr_t)__bss_start__;cursor<(uintptr_t)__bss_end__;cursor+=sizeof(uint32_t))
        *(volatile uint32_t *)cursor=0;
    (void)main();
    for (;;) {}
}
