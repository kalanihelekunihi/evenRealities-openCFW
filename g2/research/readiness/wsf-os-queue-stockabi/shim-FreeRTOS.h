#ifndef OPENCFW_SCRATCH_FREERTOS_H
#define OPENCFW_SCRATCH_FREERTOS_H

#include <stdint.h>

typedef int32_t BaseType_t;
typedef uint32_t TickType_t;
typedef uint32_t EventBits_t;

#define pdFALSE ((BaseType_t)0)
#define pdTRUE ((BaseType_t)1)
#define pdFAIL ((BaseType_t)0)
#define pdPASS ((BaseType_t)1)
#define portMAX_DELAY ((TickType_t)0xffffffffUL)

BaseType_t xPortIsInsideInterrupt(void);
void vPortYield(void);

#define portYIELD() vPortYield()
#define portYIELD_FROM_ISR(required)                                            \
    do {                                                                        \
        if ((required) != pdFALSE) {                                            \
            *((volatile uint32_t *)0xe000ed04UL) = (1UL << 28);                \
        }                                                                       \
    } while (0)

#endif
