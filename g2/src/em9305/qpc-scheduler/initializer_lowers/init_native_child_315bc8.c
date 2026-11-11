#include <stdint.h>

/* Native 0x315bc8..0x315c0c: clear the record's pending word (+640) and
 * keep only bit 17 of the flag word (+636); if that bit was set, clear
 * both words and report mode event 0x3b. If the reject byte (+627) is set,
 * clear it and send PHY reject 0x3b (extended). */
extern uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t context,uint32_t status);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t record,uint32_t reason,
                                                 uint32_t extended);

void opencfw_em9305_child_315bc8(uintptr_t record)
{
    uint32_t flags=*(volatile uint32_t *)(record+636u);
    *(volatile uint32_t *)(record+640u)=0u;
    flags&=0x20000u;
    *(volatile uint32_t *)(record+636u)=flags;
    if(flags!=0u){
        *(volatile uint32_t *)(record+640u)=0u;
        *(volatile uint32_t *)(record+636u)=0u;
        (void)opencfw_em9305_mode_event_322fdc(record,0x3bu);
    }
    if(*(volatile uint8_t *)(record+627u)!=0u){
        *(volatile uint8_t *)(record+627u)=0u;
        (void)opencfw_em9305_phy_reject_32698c(record,0x3bu,1u);
    }
}
