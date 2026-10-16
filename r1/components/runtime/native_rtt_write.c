#include <stdint.h>
#include "SEGGER_RTT.h"
/* Native wrapper around authenticated SEGGER RTT 6.18a ring writing.
 * Initialization is the existing source-owned native initializer, not the
 * generic upstream initializer. MRS/MSR privilege effects remain hardware. */
uint32_t r1_stdout_write(uint32_t channel,volatile void *buffer,uint32_t length)
{
    if (*(volatile unsigned char *)&_SEGGER_RTT.acID[0]!='S') SEGGER_RTT_Init();
    uint32_t previous;
    __asm__ volatile("mrs %0, BASEPRI" : "=r"(previous) : : "memory");
    uint32_t mask=32;
    __asm__ volatile("msr BASEPRI, %0" : : "r"(mask) : "memory");
    uint32_t status=SEGGER_RTT_WriteNoLock(channel,(const void *)buffer,length);
    register uint32_t restored __asm__("r1")=(uint8_t)previous;
    __asm__ volatile("msr BASEPRI, %0" : : "r"(restored) : "memory");
    register uint32_t result __asm__("r0")=status;
    __asm__ volatile("" : "+r"(result),"+r"(restored) : : "memory");
    return result;
}
