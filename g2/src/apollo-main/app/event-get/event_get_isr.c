/* Native xEventGroupGetBitsFromISR 0x47ed64..0x47ed75.
 * The two children are architectural BASEPRI mask/restore 0x5fa0a4/ba. */
#include <stdint.h>
uint32_t audio_uart_event_get_isr(void *event)
{
    uint32_t previous,threshold=0x30u;
    __asm__ volatile("mrs %0, basepri\n\tmsr basepri, %1\n\tdsb\n\tisb"
                     :"=&r"(previous):"r"(threshold):"memory");
    uint32_t bits=*(volatile uint32_t *)event;
    __asm__ volatile("msr basepri, %0\n\tdsb\n\tisb"::"r"(previous):"memory");
    return bits;
}
