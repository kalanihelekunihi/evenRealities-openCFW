/* Native CMSIS osThreadYield 0x4491e4 and port yield 0x4420bc. */
#include <stdint.h>
extern uint32_t audio_irq_context(void); /* selected IRQ_Context 0x44900e */
int32_t audio_ble_thread_yield(void) {
    if(audio_irq_context()!=0u) return -6;
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    __asm__ volatile("dsb sy\n\tisb sy" ::: "memory");
    return 0;
}
