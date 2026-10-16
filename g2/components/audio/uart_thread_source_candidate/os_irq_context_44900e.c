/* Apollo main 0x44900e: CMSIS-FreeRTOS IRQ_Context. */
#include <stdint.h>

extern uint32_t audio_os_scheduler_state_4558a4(void);

uint32_t audio_os_irq_context_44900e(void) {
    uint32_t ipsr;
    __asm volatile("mrs %0, IPSR" : "=r"(ipsr));
    if (ipsr != 0u) return 1u;
    if (audio_os_scheduler_state_4558a4() == 1u) return 0u;
    uint32_t primask;
    __asm volatile("mrs %0, PRIMASK" : "=r"(primask));
    if (primask != 0u) return 1u;
    uint32_t basepri;
    __asm volatile("mrs %0, BASEPRI" : "=r"(basepri));
    return basepri != 0u ? 1u : 0u;
}
