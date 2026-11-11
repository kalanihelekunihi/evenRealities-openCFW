#include <stdint.h>

/* Native 0x32a780..0x32aa48: start an advertising set (record at adv)
 * with an optional duration timeout (ms). Clears and seeds the event
 * object at +2264 (callbacks 32a770/32aa9c, channel map +2312), selects
 * the TX power (+60, or the default at 0x805a9c when 0x7f, capped by
 * 0x805bf0), the access address/CRC init, the PHY code and the packet
 * length fields from the event properties (+32) and options (+59), the
 * channel selection (+2439/+2438, random when bit 6 of 0x805a85), builds
 * the advertising PDU (324278, 32387c or the hook at 0x805174) and, for
 * connectable/scannable legacy sets, the response handlers and scan
 * response (324354). It then schedules the event (timeout via 312f88,
 * else 313220) and arms the high-duty/directed/extended follow-up
 * (3282c4, 328594, 32841c) before 32c650. Returns 0, 0x12 when it cannot
 * be scheduled or 0x1f when no event buffer is free. */
extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);
extern void opencfw_em9305_child_32a770(void);
extern void opencfw_em9305_child_32aa9c(void);
extern void opencfw_em9305_child_32c1d4(void);
extern void opencfw_em9305_child_32c178(void);
extern uint32_t opencfw_em9305_child_32c650(uintptr_t event, uint32_t time);
extern uint32_t opencfw_em9305_scan_random_30c478(void);
extern uint32_t opencfw_em9305_child_324278(uintptr_t record, uintptr_t buffer);
extern uint32_t opencfw_em9305_child_32387c(uintptr_t,uintptr_t,uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_child_324354(uintptr_t record, uintptr_t buffer);
extern uint32_t opencfw_em9305_child_325854(uintptr_t record);
extern uint32_t opencfw_em9305_child_323bac(uintptr_t,uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t object, uint32_t seed);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);
extern uint32_t opencfw_em9305_associated_time_alias_30fd34(void);
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_init_schedule_adjust_312f88(uintptr_t object, uint32_t minimum,
                                                           uint32_t step);
extern uint32_t opencfw_em9305_child_3282c4(uintptr_t record);
extern uint32_t opencfw_em9305_child_328594(uintptr_t record);
extern uint32_t opencfw_em9305_child_32841c(uintptr_t record);

uint32_t opencfw_em9305_child_32a780(uintptr_t adv, uint32_t timeout)
{
    volatile uint8_t *a=(volatile uint8_t *)adv;
    uintptr_t event=adv+2264u;
    (void)opencfw_em9305_memset((void *)event,0u,0x94u);
    int32_t power=(int8_t)a[60];
    a[2290]=1u;
    a[2288]=3u;
    a[2312]=3u;
    *(volatile uint32_t *)(adv+2300u)=(uint32_t)adv;
    *(volatile uint32_t *)(adv+2296u)=(uint32_t)(uintptr_t)opencfw_em9305_child_32a770;
    *(volatile uint32_t *)(adv+2292u)=(uint32_t)(uintptr_t)opencfw_em9305_child_32aa9c;
    *(volatile uint32_t *)(adv+2308u)=(uint32_t)(adv+2312u);
    if(power==0x7f)power=*(volatile int8_t *)(uintptr_t)0x805a9cu;
    uint32_t phy_index=a[68]-1u;
    int32_t limit=*(volatile int8_t *)(uintptr_t)0x805bf0u;
    uint32_t channels=a[61];
    *(volatile uint32_t *)(adv+2320u)=0x555555u;
    uint32_t properties=*(volatile uint16_t *)(adv+32u);
    a[2325]=(uint8_t)channels;
    a[2324]=(uint8_t)channels;
    int32_t level=power<limit?power:limit;
    uint32_t phy_code=phy_index<4u?(uint8_t)(0x2010201u>>((uint8_t)phy_index*8u)):0u;
    *(volatile uint32_t *)(adv+2316u)=0x8e89bed6u;
    *(volatile uint16_t *)(adv+2388u)=0x28u;
    a[2314]=(uint8_t)level;
    a[2327]=(uint8_t)phy_code;
    a[2326]=(uint8_t)phy_code;
    if((properties&4u)!=0u){
        *(volatile uint32_t *)(adv+2392u)=4u;
    }else{
        uint32_t length=0x20u;
        if((properties&2u)!=0u&&(a[59]&1u)!=0u){
            length=0x28u;
            *(volatile uint16_t *)(adv+2390u)=8u;
        }
        if((properties&1u)!=0u&&(a[59]&2u)!=0u)
            *(volatile uint16_t *)(adv+2390u)=(uint16_t)length;
    }
    uint32_t options=*(volatile uint8_t *)(uintptr_t)0x805a85u;
    uint32_t channel=a[56];
    *(volatile uint32_t *)(adv+2424u)=(uint32_t)(uintptr_t)opencfw_em9305_child_32c650;
    a[2439]=(uint8_t)channel;
    uint32_t selection=0u;
    if((options&0x40u)!=0u){
        selection=opencfw_em9305_scan_random_30c478();
        properties=*(volatile uint16_t *)(adv+32u);
        selection&=3u;
    }
    a[2438]=(uint8_t)selection;
    uint32_t built;
    if((properties&0x10u)!=0u){
        if((properties&0x1du)==0x1du){
            uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cbcu;
            *(volatile uint32_t *)(adv+36u)=0u;
            a[2438]=0u;
            *(volatile uint32_t *)(adv+40u)=0xea6u;
            *(volatile uint32_t *)(adv+44u)=*(volatile uint32_t *)(config+4u)*1000u;
        }
        built=opencfw_em9305_child_324278(adv,adv+840u);
        a[2436]=(uint8_t)built;
    }else if((properties&0x80u)!=0u){
        uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x805174u;
        if(hook!=0u){
            built=((uint32_t (*)(uintptr_t,uintptr_t,uintptr_t,uint32_t))hook)
                (adv,adv+840u,adv+1972u,0u);
            a[2436]=(uint8_t)built;
        }
    }else{
        built=opencfw_em9305_child_32387c(adv,adv+840u,0u);
        a[2436]=(uint8_t)built;
    }
    properties=*(volatile uint16_t *)(adv+32u);
    *(volatile uint32_t *)(adv+2412u)=(uint32_t)(adv+840u);
    if((properties&0x10u)!=0u&&(properties&3u)!=0u){
        uintptr_t message=opencfw_em9305_wsf_event_allocate(0x28u);
        if(message==0u)return 0x1fu;
        uint32_t legacy=a[32];
        *(volatile uint32_t *)(adv+2432u)=(uint32_t)(uintptr_t)opencfw_em9305_child_32c1d4;
        *(volatile uint32_t *)(adv+2428u)=(uint32_t)(uintptr_t)opencfw_em9305_child_32c178;
        *(volatile uint32_t *)(adv+2416u)=(uint32_t)(message+4u);
        if((legacy&2u)!=0u){
            uintptr_t response=adv+906u;
            a[2437]=(uint8_t)opencfw_em9305_child_324354(adv,response);
            *(volatile uint32_t *)(adv+2420u)=(uint32_t)response;
        }
    }
    (void)opencfw_em9305_child_325854(adv);
    uintptr_t periodic=*(volatile uint32_t *)(adv+828u);
    if(periodic!=0u)(void)opencfw_em9305_child_323bac(adv,0u,a[2784],periodic);
    (void)opencfw_em9305_associated_object_init_312918(event,0u);
    if(*(volatile uint32_t *)(*(volatile uint32_t *)(uintptr_t)0x805cbcu+4u)!=0u){
        uint32_t offset=opencfw_em9305_associated_time_alias_30fd34();
        uint32_t now=opencfw_em9305_scan_current_303f80();
        uint32_t step=timeout*1000u;
        *(volatile uint32_t *)(adv+2272u)=now+offset;
        if(opencfw_em9305_init_schedule_adjust_312f88(event,0u,step)==0u)return 0x12u;
    }else{
        (void)opencfw_em9305_auxiliary_insert_313220(event);
    }
    if(*(volatile uint32_t *)(adv+828u)==0u)return 0u;
    uint32_t mode=*(volatile uint16_t *)(adv+32u)&3u;
    if(mode==3u)return 0x12u;
    if(mode==1u){
        if(*(volatile uint8_t *)(*(volatile uint32_t *)(uintptr_t)0x805cacu+34u)==0u)return 0x12u;
        (void)opencfw_em9305_child_3282c4(adv);
    }else if(mode==2u){
        (void)opencfw_em9305_child_328594(adv);
    }else{
        (void)opencfw_em9305_child_32841c(adv);
    }
    uint32_t time=*(volatile uint32_t *)(adv+2272u);
    a[2785]=1u;
    (void)opencfw_em9305_child_32c650(event,time);
    return 0u;
}
