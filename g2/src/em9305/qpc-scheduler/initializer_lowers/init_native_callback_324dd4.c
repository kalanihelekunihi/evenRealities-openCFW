#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x324dd4..0x324e3a: privacy work-item callback. Kind 1 refreshes
 * every resolving-list address and restarts the command timer; kind 3
 * refreshes all entries (zero identity) or the matching one; kind 2
 * resolves (+4 set) or projects an address from {+16, +20, +5, +8} and
 * then retires one outstanding item (((uintptr_t)&em9305_ram_805af0 + 0x6cu)) in a critical section. */
extern void opencfw_em9305_child_303a80(void);
extern uint32_t opencfw_em9305_command_timer_325268(void);
extern void opencfw_em9305_child_303ad8(uint32_t type, uint32_t low, uint32_t high);
extern uint32_t opencfw_em9305_radio_resolve_303bdc(uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_address_project_303b7c(uint32_t,uint32_t,uintptr_t,uintptr_t);
extern void opencfw_em9305_wsf_critical_enter(void);
extern void opencfw_em9305_wsf_critical_exit(void);

void opencfw_em9305_callback_324dd4(uintptr_t item)
{
    uint32_t kind=*(volatile uint8_t *)(item+3u);
    if(kind==3u){
        uint32_t low=*(volatile uint32_t *)(item+8u);
        uint32_t high=*(volatile uint32_t *)(item+12u);
        if((low|high)==0u)opencfw_em9305_child_303a80();
        else opencfw_em9305_child_303ad8(*(volatile uint8_t *)(item+5u),low,high);
        return;
    }
    if(kind==2u){
        uint32_t resolve=*(volatile uint8_t *)(item+4u);
        uint32_t first=*(volatile uint32_t *)(item+16u);
        uint32_t second=*(volatile uint32_t *)(item+20u);
        if(resolve!=0u)
            (void)opencfw_em9305_radio_resolve_303bdc(first,second,item+5u,item+8u);
        else
            (void)opencfw_em9305_radio_address_project_303b7c(first,second,item+5u,item+8u);
        opencfw_em9305_wsf_critical_enter();
        volatile uint8_t *outstanding=&em9305_ram_805af0.u8_805b5c;
        *outstanding=(uint8_t)(*outstanding-1u);
        opencfw_em9305_wsf_critical_exit();
        return;
    }
    if(kind==1u){
        opencfw_em9305_child_303a80();
        (void)opencfw_em9305_command_timer_325268();
    }
}
