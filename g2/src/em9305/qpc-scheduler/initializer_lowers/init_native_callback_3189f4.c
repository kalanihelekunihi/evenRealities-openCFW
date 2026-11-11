#include <stdint.h>

/* Native 0x3189f4..0x318ab8: a new local address {low, high}. For every
 * active 912-byte record (config byte 34 records from *0x805c70): records
 * with an address already set (+2) update the cached address at 0x8012d8
 * when it changed, restamping the record's anchor (+240) first when its
 * flags (+548 bit 7) and timer (+565) say so. Records without one notify
 * the hook at *0x801314, run 307434 and send event 0x1601 {record, low,
 * high} to the task at 0x805b18. Returns 0x0c if 307434 fails or no
 * 12-byte message is available, else 0. The stock hook call leaves the
 * hook address in r1. */
extern uint32_t opencfw_em9305_associated_time_alias_30fd34(void);
extern uint32_t opencfw_em9305_child_307434(uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);

uint32_t opencfw_em9305_callback_3189f4(uint32_t low,uint32_t high)
{
    volatile uint32_t *cached=(volatile uint32_t *)(uintptr_t)0x8012d8u;
    for(uint32_t index=0u;;++index) {
        uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
        if(index>=*(volatile uint8_t *)(config+34u)) return 0u;
        uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
        uintptr_t record=base+index*912u;
        if(*(volatile uint8_t *)record==0u) continue;
        if(*(volatile uint8_t *)(record+2u)!=0u) {
            if(((cached[0]^low)|(cached[1]^high))==0u) continue;
            if((*(volatile uint8_t *)(record+548u)&0x80u)!=0u&&
               *(volatile uint8_t *)(record+565u)!=0u)
                *(volatile uint32_t *)(record+240u)=opencfw_em9305_associated_time_alias_30fd34();
            cached[0]=low;
            cached[1]=high;
            continue;
        }
        uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x801314u;
        if(hook!=0u) ((void (*)(uint32_t,uintptr_t))hook)((uint16_t)index,hook);
        if(opencfw_em9305_child_307434((uint16_t)index,0x16u)!=0u) return 0x0cu;
        uintptr_t message=opencfw_em9305_wsf_event_allocate(12u);
        if(message==0u) return 0x0cu;
        *(volatile uint16_t *)(message+2u)=0x1601u;
        uint32_t task=*(volatile uint8_t *)(uintptr_t)0x805b18u;
        *(volatile uint32_t *)(message+4u)=low;
        *(volatile uint32_t *)(message+8u)=high;
        *(volatile uint16_t *)message=(uint16_t)index;
        (void)opencfw_em9305_wsf_task_message_send(task,message);
    }
}
