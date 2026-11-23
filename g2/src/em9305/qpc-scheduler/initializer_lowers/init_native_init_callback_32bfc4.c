#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32bfc4..0x32c148: build the periodic-advertising report for
 * subevent data slot `index` of the owner's context (+44, data pointer at
 * +208 + 4*index) on its link (+36, report object at +2812).
 * Without data and a pending report (+64 == 1) a "no data" report is
 * prepared (TX power/RSSI 0x7f, status 2) with the event counter derived
 * from the elapsed time. With data and no pending report, a report is
 * prepared unless the slot is late (+236 - +240 >= link +700): handle,
 * subevent, optional TX power (+29) and CTE (+25) per ((uintptr_t)&em9305_ram_805688 + 0x44u), RSSI
 * (+227), the rounded event counter, and either the payload (when the
 * counter falls in the response window of the channel map at +1160) or
 * status 0xff. A role-1 link (+368) marks the report pending. Both
 * prepared cases finish through 3247d4. */
extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t length);
extern uint32_t opencfw_em9305_dispatch_child_3247d4(uintptr_t link);

static uint32_t opencfw_em9305_round_count_32bfc4(uint32_t elapsed, uint32_t interval)
{
    uint32_t count=elapsed/interval;
    uint32_t remainder=elapsed-interval*(uint8_t)count;
    return count+(remainder>=(interval>>1));
}

void opencfw_em9305_init_callback_32bfc4(uintptr_t owner, uint32_t index)
{
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    uintptr_t context=*(volatile uint32_t *)(owner+44u);
    volatile uint32_t *slot=(volatile uint32_t *)(link+2812u);
    uintptr_t report=*slot;
    volatile uint8_t *r=(volatile uint8_t *)report;
    volatile const uint8_t *timing=(volatile const uint8_t *)(link+796u);
    uintptr_t data=*(volatile uint32_t *)(context+208u+index*4u);
    uint32_t pending=r[64];
    if(data==0u){
        if(pending!=1u)return;
        (void)opencfw_em9305_memset((void *)(report+44u),0u,20u);
        *(volatile uint16_t *)(report+52u)=0x7f7fu;
        uint32_t offset=timing[0];
        uint32_t interval=timing[1]*125u;
        uint32_t elapsed=*(volatile uint32_t *)(context+180u)-*(volatile uint32_t *)(link+800u)
                         -offset*1250u;
        r[56]=2u;
        r[54]=0xffu;
        r[51]=1u;
        r[55]=(uint8_t)opencfw_em9305_round_count_32bfc4(elapsed,interval);
        (void)opencfw_em9305_dispatch_child_3247d4(link);
        return;
    }
    if(pending!=0u){
        (void)opencfw_em9305_dispatch_child_3247d4(link);
        return;
    }
    uint32_t options=em9305_ram_805688.u8_8056cc;
    (void)opencfw_em9305_memset((void *)(report+44u),0u,20u);
    if(*(volatile uint32_t *)(context+236u)-*(volatile uint32_t *)(context+240u)>=
       *(volatile uint32_t *)(link+700u)){
        (void)opencfw_em9305_dispatch_child_3247d4(link);
        return;
    }
    uint32_t handle=*(volatile uint8_t *)(link+1u);
    uint32_t subevent=timing[3];
    r[51]=1u;
    r[48]=(uint8_t)handle;
    r[49]=(uint8_t)subevent;
    uint32_t power=0u;
    if((options&0x40u)!=0u)power=*(volatile uint8_t *)(*slot+29u);
    r[52]=(uint8_t)power;
    uint32_t cte=0xffu;
    r[53]=*(volatile uint8_t *)(context+227u);
    if((options&4u)!=0u)cte=*(volatile uint8_t *)(*slot+25u);
    uint32_t offset=timing[0];
    uint32_t since=*(volatile uint32_t *)(context+180u)-*(volatile uint32_t *)(link+800u);
    uint32_t elapsed=since-offset*1250u;
    uint32_t interval=timing[1]*125u;
    if(since<elapsed)elapsed=0u;
    uintptr_t map=*(volatile uint32_t *)(link+1160u);
    r[54]=(uint8_t)cte;
    uint32_t count=opencfw_em9305_round_count_32bfc4(elapsed,interval);
    uint32_t first=*(volatile uint8_t *)(map+0xf00u);
    r[55]=(uint8_t)count;
    count=(uint8_t)count;
    if(count<first||count>=first+*(volatile uint8_t *)(map+0xf01u)){
        r[56]=0xffu;
    }else{
        uintptr_t current=*slot;
        uintptr_t source=*(volatile uint32_t *)(context+208u+index*4u)
                         +*(volatile uint8_t *)(current+4u)+3u;
        (void)opencfw_em9305_memcpy((void *)*(volatile uint32_t *)current,(const void *)source,
                                    em9305_ram_805688.u8_8056d4);
        current=*slot;
        uint32_t length=em9305_ram_805688.u8_8056d4;
        r[56]=0u;
        uint32_t buffer=*(volatile uint32_t *)current;
        r[57]=(uint8_t)length;
        *(volatile uint32_t *)(report+60u)=buffer;
    }
    if(*(volatile uint8_t *)(link+368u)==1u)*(volatile uint8_t *)(*slot+64u)=1u;
    (void)opencfw_em9305_dispatch_child_3247d4(link);
}
