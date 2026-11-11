#include <stdint.h>

/* Native 0x31c7c4..0x31c88c: arm a periodic-sync/associated receive
 * from the parameter block {+0 options, +1 clock accuracy, +2 skip-less
 * flag, +4 interval units, +6 PHY}. Unsupported PHYs return 0. Latches
 * the options (+533) and, when bit 6 of +154 is set, +177 into +534;
 * stores the PHY code (1/2/3) at +544/+545; computes the window
 * (30 or 300 x units) and the widened offset from 317ebc, sets the anchor
 * (+492) and window (+660) of the object at +484 and either inserts it
 * (marking +241) or, when the first anchor is too close for the scan
 * window, flags +700. */
extern uint32_t opencfw_em9305_child_31b794(uint32_t selector);
extern uint32_t opencfw_em9305_init_secondary_current_303f5c(void);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t object, uint32_t seed);
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);

uint32_t opencfw_em9305_child_31c7c4(uintptr_t record, uintptr_t parameters, uint32_t start)
{
    volatile const uint8_t *p=(volatile const uint8_t *)parameters;
    if(opencfw_em9305_child_31b794((uint8_t)(p[6]+1u))==0u)return 0u;
    uint32_t sca_flags=*(volatile uint8_t *)(record+154u);
    *(volatile uint8_t *)(record+533u)=p[0];
    if((sca_flags&0x40u)!=0u)
        *(volatile uint8_t *)(record+534u)=*(volatile uint8_t *)(record+177u);
    uint32_t phy=p[6];
    uint32_t skip=p[2];
    uint32_t units=*(volatile const uint16_t *)(parameters+4u);
    uint32_t code=phy==2u?3u:(phy==1u)+1u;
    uint32_t window=(skip==0u?30u:300u)*units;
    *(volatile uint8_t *)(record+545u)=(uint8_t)code;
    *(volatile uint8_t *)(record+544u)=(uint8_t)code;
    uint32_t now=opencfw_em9305_init_secondary_current_303f5c();
    uint32_t margin=p[2]==0u?30u:300u;
    uint32_t drift=p[1]==1u?50u:500u;
    uint32_t widening=opencfw_em9305_init_secondary_time_317ebc(margin+window,now+drift);
    uint32_t offset=window-widening;
    uint32_t span=(p[2]==0u?30u:300u)+2u*widening;
    uintptr_t object=record+484u;
    *(volatile uint32_t *)(record+492u)=start+offset;
    *(volatile uint32_t *)(record+660u)=span;
    (void)opencfw_em9305_associated_object_init_312918(object,0u);
    uint32_t scan=opencfw_em9305_scan_current_303f80();
    if(offset<scan){
        *(volatile uint8_t *)(record+700u)=1u;
        return scan;
    }
    uint32_t inserted=opencfw_em9305_associated_schedule_insert_312da4(object,0u);
    if(inserted!=0u)*(volatile uint8_t *)(record+241u)=1u;
    return inserted;
}
