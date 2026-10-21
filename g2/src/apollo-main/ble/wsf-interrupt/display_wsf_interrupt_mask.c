/* Native FreeRTOS ulSetInterruptMask 0x5fa0a4. */
#include <stdint.h>
uint32_t audio_wsf_interrupt_mask_set(void) {
    uint32_t old;
    uint32_t mask=0x30u;
    __asm__ volatile("mrs %0, basepri\n"
                     "msr basepri, %1\n"
                     "dsb sy\n"
                     "isb sy\n"
                     : "=&r"(old) : "r"(mask) : "memory");
    return old;
}
