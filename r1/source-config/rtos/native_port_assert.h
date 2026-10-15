#ifndef R1_NATIVE_PORT_ASSERT_H
#define R1_NATIVE_PORT_ASSERT_H
/* Translation-unit override for selected authenticated native port, task and CMSIS variants.
 * Stock critical assertions mask BASEPRI, write zero at 0xFFFFFFFF, then loop.
 * The baseline kernel/SDK objects retain their existing configurations. */
#include <stdint.h>
#undef configASSERT
#define configASSERT(condition) do { if (!(condition)) { \
    portDISABLE_INTERRUPTS(); \
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0; \
    for (;;) {} \
} } while (0)
#include "FreeRTOS.h"
#endif
