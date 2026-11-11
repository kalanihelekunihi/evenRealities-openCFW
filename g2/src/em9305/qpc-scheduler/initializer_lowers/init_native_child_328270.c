#include <stdint.h>

/* Native 0x328270..0x3282c2: initialise the associated object (seed byte
 * +76 when +1432 is clear), then, when the count byte +62 is set, raise
 * the window at +836 to min(count * interval(+36) + 10000, 0x257ed4) if
 * that exceeds the floor at +2276, and continue with 3284ec. */
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t object, uint32_t seed);
extern uint32_t opencfw_em9305_child_3284ec(uintptr_t record, uintptr_t object);

uint32_t opencfw_em9305_child_328270(uintptr_t record, uintptr_t object)
{
    uint32_t seed=0u;
    if(*(volatile uint8_t *)(record+1432u)==0u)seed=*(volatile uint8_t *)(record+76u);
    (void)opencfw_em9305_associated_object_init_312918(object,seed);
    uint32_t count=*(volatile uint8_t *)(record+62u);
    if(count!=0u){
        uint32_t window=*(volatile uint32_t *)(record+36u)*count+10000u;
        uint32_t floor=*(volatile uint32_t *)(record+2276u);
        if(window>0x257ed4u)window=0x257ed4u;
        if(window>floor)floor=window;
        *(volatile uint32_t *)(record+836u)=floor;
    }
    return opencfw_em9305_child_3284ec(record,object);
}
