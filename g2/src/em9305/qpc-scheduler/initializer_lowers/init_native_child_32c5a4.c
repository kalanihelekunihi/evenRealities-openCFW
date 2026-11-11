#include <stdint.h>

/* Native 0x32c5a4..0x32c64e: build the next associated packet for the
 * link at +36. Without a pending length (+2780) only a fresh start goes
 * on. Latches +2784 into +2517 and returns pending + the configured
 * overhead (+22 of 0x805cac; 0 when skipped). A fresh start resets the
 * offset (+1706) and builds the first packet (323c0c) into
 * {+2636 length, +2644 offset, +2648 base}; a continuation flushes when
 * the offset is below +2248, continues (323ac8) and records
 * {+2652 length, +2660 consumed, +2664 position}. */
extern uint32_t opencfw_em9305_child_325854(uintptr_t link);
extern uint32_t opencfw_em9305_associated_packet_continue_323ac8(uintptr_t,uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_323c0c(uintptr_t link, uintptr_t buffer, uint32_t flags);

uint32_t opencfw_em9305_child_32c5a4(uintptr_t owner, uint32_t continuing)
{
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    uint32_t pending=*(volatile uint32_t *)(link+2780u);
    if(pending==0u&&continuing!=0u)return 0u;
    uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uint32_t latched=*(volatile uint8_t *)(link+2784u);
    uint32_t total=pending+*(volatile uint16_t *)(config+22u);
    volatile uint16_t *offset=(volatile uint16_t *)(link+1706u);
    *(volatile uint8_t *)(link+2517u)=(uint8_t)latched;
    if(continuing==0u){
        *offset=0u;
        (void)opencfw_em9305_child_325854(link);
        uint32_t length=opencfw_em9305_child_323c0c(link,link+1011u,0u);
        uint32_t position=*offset;
        uint32_t base=*(volatile uint32_t *)(link+1700u);
        *(volatile uint16_t *)(link+2636u)=(uint16_t)length;
        *(volatile uint16_t *)(link+2644u)=(uint16_t)position;
        *(volatile uint32_t *)(link+2648u)=base;
        return total;
    }
    uint32_t start=*offset;
    if(start<*(volatile uint16_t *)(link+2248u))(void)opencfw_em9305_child_325854(link);
    uint32_t length=opencfw_em9305_associated_packet_continue_323ac8(link,link+1011u,link+1696u,0u);
    uint32_t position=*offset;
    uint32_t base=*(volatile uint32_t *)(link+1700u);
    *(volatile uint16_t *)(link+2652u)=(uint16_t)length;
    *(volatile uint16_t *)(link+2660u)=(uint16_t)(position-start);
    *(volatile uint32_t *)(link+2664u)=start+base;
    return total;
}
