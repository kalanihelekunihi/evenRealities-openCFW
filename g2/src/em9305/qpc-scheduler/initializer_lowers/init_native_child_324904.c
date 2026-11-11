#include <stdint.h>

/* Native 0x324904..0x324964: periodic-advertising slot event for the
 * 784-byte slot (event +6) of the table at 0x803f70. Kind 2 clears the
 * slot's first byte, kind 1 the byte at -96. Kind 0 commits a pending
 * channel map when the event's window (+2) reaches the slot's due count
 * (-180) minus the event count (+0, signed): copy the staged map words
 * (-188, -184) to +140/+144, transform them and clear the staged flag
 * (-192). */
extern uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t);

void opencfw_em9305_child_324904(uintptr_t event)
{
    uint32_t kind=*(volatile uint8_t *)(event+4u);
    uintptr_t slot=(uintptr_t)0x803f70u+*(volatile uint16_t *)(event+6u)*784u;
    if(kind==2u) {
        *(volatile uint8_t *)slot=0u;
        return;
    }
    if(kind==1u) {
        *(volatile uint8_t *)(slot-96u)=0u;
        return;
    }
    if(kind!=0u) return;
    uint32_t count=*(volatile uint16_t *)event;
    uint32_t window=*(volatile uint16_t *)(event+2u);
    uint32_t due=*(volatile uint16_t *)(slot-180u);
    if((int32_t)window<(int32_t)(due-count)) return;
    uint32_t high=*(volatile uint32_t *)(slot-184u);
    uint32_t low=*(volatile uint32_t *)(slot-188u);
    *(volatile uint32_t *)(slot+144u)=high;
    *(volatile uint32_t *)(slot+140u)=low;
    (void)opencfw_em9305_radio_channel_transform_30e3fc(slot+140u);
    *(volatile uint8_t *)(slot-192u)=0u;
}
