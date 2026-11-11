#include <stdint.h>
#include "../board/native_battery_memory.h"

extern volatile uint8_t r1_wear_adt_history[20],r1_wear_adt_active;
extern volatile uint32_t r1_wear_adt_count;

uint32_t r1_wear_optical_history_range(void)
{
    uint32_t previous=r1_wear_adt_count;
    /* Stock converts the nonzero uint32 to binary64 and back exactly. */
    uint32_t minimum=previous?previous:UINT32_C(1000000000);
    uint32_t maximum=previous;
    uint32_t count=r1_wear_adt_active;
    for (uint32_t index=0;index<count;index=(uint8_t)(index+1u)) {
        uintptr_t address=(uintptr_t)r1_wear_adt_history+index*4u;
        uint32_t value=read32((const volatile uint8_t *)address);
        if (value<minimum) minimum=value;
        if (value>maximum) maximum=value;
    }
    return maximum-minimum;
}
