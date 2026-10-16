/* Apollo main 0x5fa0a4: FreeRTOS interrupt priority mask leaf. */
#include <stdint.h>

uint64_t audio_os_interrupt_mask_5fa0a4(void) {
    uint32_t previous;
    uint32_t mask = 0x30u;
    __asm volatile("mrs %0, BASEPRI" : "=r"(previous));
    __asm volatile("msr BASEPRI, %0" :: "r"(mask) : "memory");
    __asm volatile("dsb sy\n\tisb sy" ::: "memory");
    return ((uint64_t)mask << 32) | previous;
}
