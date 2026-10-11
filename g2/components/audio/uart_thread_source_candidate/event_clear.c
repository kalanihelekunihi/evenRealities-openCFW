/* Native CMSIS osEventFlagsClear 0x449642..0x449693. */
#include <stdint.h>
extern uint32_t audio_irq_context(void);
extern uint32_t audio_uart_event_get_isr(void *); /* 0x47ed64 */
extern uint32_t audio_uart_event_clear_isr(void *,uint32_t); /* 0x47ed52 */
extern uint32_t audio_uart_event_clear_task(void *,uint32_t); /* 0x47ed10 */
uint32_t audio_uart_event_clear(void *event,uint32_t flags)
{
    if (!event || (flags&0xff000000u)) return 0xfffffffcu;
    if (audio_irq_context()!=0u) {
        uint32_t previous=audio_uart_event_get_isr(event);
        if (!audio_uart_event_clear_isr(event,flags)) return 0xfffffffdu;
        *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
        return previous;
    }
    return audio_uart_event_clear_task(event,flags);
}
