/* Native timing children 0x47dcb4/0x47dc74 for persistence records. */
#include <stdint.h>
extern volatile uint32_t audio_uart_ring_persist_last_tick; /* RAM 0x20074ac8 */
extern volatile uint32_t audio_uart_ring_persist_wrap_count; /* RAM 0x20074ac4 */
extern uint32_t audio_uart_ring_kernel_state(void); /* osKernelGetState */
extern uint32_t audio_uart_ring_rtc_refresh(void); /* service_time_rtc_refresh */
extern uint32_t audio_tick(void); /* selected xTaskGetTickCount 0x454efe */
extern uint64_t audio_uart_ring_u64_div_47cc60(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t audio_uart_ring_persist_early_check_47dcb4(uint8_t *early) {
    if(audio_uart_ring_kernel_state()==2u) {
        uint32_t rtc=audio_uart_ring_rtc_refresh();
        *early=(uint8_t)((0x9a6dff80u+rtc)<0x8ef45680u);
        return rtc;
    }
    *early=0u;
    return 0u;
}
uint32_t audio_uart_ring_persist_clock_snapshot_47dc74(void) {
    uint32_t saved;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(saved) :: "memory");
    uint32_t now=audio_tick();
    if(now<audio_uart_ring_persist_last_tick)audio_uart_ring_persist_wrap_count++;
    audio_uart_ring_persist_last_tick=now;
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    return audio_uart_ring_u64_div_47cc60(now,audio_uart_ring_persist_wrap_count,1000u,0u);
}
