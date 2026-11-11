/* Source-built application reset. The old scatter descriptors refer to
 * absolute stock-image addresses and cannot initialize a relinked image. */
#include <stdint.h>

extern void SystemInit(void);
extern void r1_native_runtime_entry(void);
extern uint8_t __etext[];
extern uint8_t __data_start__[];
extern uint8_t __r1_data_init_end__[];
extern uint8_t __bss_start__[];
extern uint8_t __bss_end__[];

_Noreturn void Reset_Handler(void)
{
    SystemInit();
    const uint8_t *source = __etext;
    for (uint8_t *destination = __data_start__;
         destination < __r1_data_init_end__; ++destination)
        *destination = *source++;
    for (uint8_t *destination = __bss_start__; destination < __bss_end__;
         ++destination)
        *destination = 0;
    r1_native_runtime_entry();
    for (;;) { /* The application entry is expected to remain active. */ }
}
