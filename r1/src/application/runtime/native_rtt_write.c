#include <stdint.h>
#include "nrf.h"
#include "SEGGER_RTT.h"
/* Source-owned initialization and authenticated SEGGER RTT ring writing.
 * CMSIS expresses the architectural BASEPRI accesses; keep the stock mask
 * value and exact restoration rather than changing the critical-section policy. */
uint32_t r1_stdout_write(uint32_t channel,volatile void *buffer,uint32_t length)
{
    if (*(volatile unsigned char *)&_SEGGER_RTT.acID[0]!='S') SEGGER_RTT_Init();
    uint32_t previous=__get_BASEPRI();
    __set_BASEPRI(32);
    uint32_t status=SEGGER_RTT_WriteNoLock(channel,(const void *)buffer,length);
    __set_BASEPRI((uint8_t)previous);
    return status;
}
