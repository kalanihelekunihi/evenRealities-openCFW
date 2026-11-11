#include <stdint.h>

/* Native 0x3202e0..0x320312: start an auxiliary scan entry: store the scan
 * buffer (+1228) and the interval (+0x16 halfword times 625) in the record,
 * clear its two state bytes, insert its schedule node (+244) and copy the
 * resulting anchor (+252) to +0x5c. */
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);

uint32_t opencfw_em9305_child_3202e0(uintptr_t record)
{
    uint32_t scan=opencfw_em9305_scan_current_303f80();
    uint32_t interval=*(volatile uint16_t *)(record+0x16u);
    *(volatile uint32_t *)(record+256u)=scan+1228u;
    *(volatile uint8_t *)(record+2u)=0u;
    *(volatile uint8_t *)(record+1u)=0u;
    *(volatile uint32_t *)(record+260u)=interval*625u;
    (void)opencfw_em9305_auxiliary_insert_313220(record+244u);
    uint32_t anchor=*(volatile uint32_t *)(record+252u);
    *(volatile uint32_t *)(record+0x5cu)=anchor;
    return anchor;
}
