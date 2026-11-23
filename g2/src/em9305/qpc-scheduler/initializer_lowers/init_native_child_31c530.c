#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31c530..0x31c694: walk the received AD structures (count at
 * +762, cursor at +764). 0x32 entries go to the registered hook at
 * ((uintptr_t)&em9305_ram_805c5c + 0x4cu); for a role-1 record a 0x28 entry is decoded once into +312
 * (32da74) and a 0x2c entry into +408 (32d910), whose parameters are then
 * validated (accepted: +408 = 1, +409 = 0x2c, +410 = length; rejected:
 * +408 = 0). The cursor advances by two plus what the decoders consume,
 * the count by length + 1. */
extern uint32_t opencfw_em9305_child_32da74(uintptr_t out, uintptr_t data);
extern uint32_t opencfw_em9305_child_32d910(uintptr_t out, uintptr_t data, uint32_t length);

static uint32_t opencfw_em9305_ad_2c_valid_31c530(uintptr_t record, uint32_t minimum)
{
    if((uint32_t)(*(volatile uint8_t *)(record+424u)-1u)>=31u)return 0u;
    if(*(volatile uint32_t *)(record+448u)+0xfff00000u<0xfff00100u)return 0u;
    uint32_t value=*(volatile uint16_t *)(record+422u);
    if(value<minimum||value>=0xc81u)return 0u;
    if((uint32_t)(*(volatile uint8_t *)(record+425u)-1u)>=31u)return 0u;
    if(*(volatile uint16_t *)(record+452u)>=0x1000u)return 0u;
    if((uint32_t)(*(volatile uint16_t *)(record+442u)-1u)>250u)return 0u;
    uint32_t phy=*(volatile uint8_t *)(record+464u);
    if(phy>=4u)return 0u;
    uint32_t features=em9305_ram_805af0.u32_805b30;
    if((features&0x100u)==0u&&phy==2u)return 0u;
    if((features&0x800u)==0u&&phy==3u)return 0u;
    if(*(volatile uint8_t *)(record+476u)>=2u)return 0u;
    if((uint32_t)(*(volatile uint8_t *)(record+426u)-1u)>=7u)return 0u;
    if((uint32_t)(*(volatile uint8_t *)(record+440u)-1u)>=15u)return 0u;
    if(*(volatile uint8_t *)(record+432u)>=16u)return 0u;
    return 1u;
}

void opencfw_em9305_child_31c530(uintptr_t record)
{
    uint32_t count=*(volatile uint8_t *)(record+762u);
    if(count==0u)return;
    uintptr_t cursor=*(volatile uint32_t *)(record+764u);
    volatile uint8_t *r=(volatile uint8_t *)record;
    do{
        uint32_t type=*(volatile uint8_t *)(cursor+1u);
        uint32_t length=*(volatile uint8_t *)cursor;
        cursor+=2u;
        if(type==0x32u){
            uintptr_t hook=em9305_ram_805c5c.u32_805ca8;
            if(hook!=0u)
                ((void (*)(uintptr_t,uint32_t,uint32_t,uintptr_t))hook)(record,length,0x32u,cursor);
        }else if(type==0x2cu){
            if(r[408]==0u&&r[1]==1u){
                uint32_t used=opencfw_em9305_child_32d910(record+408u,cursor,length);
                uint32_t minimum=(em9305_ram_805a6c.u8_805a86&0x80u)!=0u?2u:4u;
                cursor+=used;
                if(opencfw_em9305_ad_2c_valid_31c530(record,minimum)!=0u){
                    r[410]=(uint8_t)length;
                    r[408]=1u;
                    r[409]=0x2cu;
                }else{
                    r[408]=0u;
                }
            }
        }else if(type==0x28u){
            uint32_t decoded=r[312];
            r[314]=(uint8_t)length;
            r[313]=0x28u;
            if(decoded==0u&&r[1]==1u){
                r[312]=1u;
                cursor+=opencfw_em9305_child_32da74(record+312u,cursor);
            }
        }
        count+=~length;
    }while((uint8_t)count!=0u);
}
