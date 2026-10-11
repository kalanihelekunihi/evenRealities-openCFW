/* CMSIS osEventFlagsSet, native 0x4495e4. Selected FreeRTOS descendants. */
#include <stdint.h>
extern uint32_t audio_irq_context(void); /* selected 0x44900e */
extern uint32_t xEventGroupSetBits(void *,uint32_t); /* selected 0x47ed76 */
extern int32_t xEventGroupSetBitsFromISR(void *,uint32_t,int32_t *); /* selected 0x47ee4a */
extern uint32_t audio_uart_event_get_isr(void *); /* selected 0x47ed64 */
uint32_t osEventFlagsSet(void *group,uint32_t bits) {
    if(group==0 || (bits&0xff000000u)!=0u) return UINT32_MAX-3u;
    if(audio_irq_context()!=0u) {
        int32_t wake=0;
        if(xEventGroupSetBitsFromISR(group,bits,&wake)==0) return UINT32_MAX-2u;
        uint32_t result=audio_uart_event_get_isr(group)|bits;
        if(wake!=0) *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
        return result;
    }
    return xEventGroupSetBits(group,bits);
}
