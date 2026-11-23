#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x327a54..0x327aaa: associated-channel event callback. For a
 * specific handle (+2 != 0xff) make the event current (((uintptr_t)&em9305_ram_805be0 + 0x54u)) and
 * update the record's channel state with the selector at +3; for the
 * broadcast handle clear the 288-byte channel block (+80) of every
 * record up to the configured count (+12 of ((uintptr_t)&em9305_ram_805c5c + 0x50u)). */
extern uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t handle);
extern uint32_t opencfw_em9305_associated_channel_state_327aac(uintptr_t record, uint32_t selector);
extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);

void opencfw_em9305_callback_327a54(uintptr_t event)
{
    if(*(volatile uint8_t *)(event+2u)!=255u){
        uintptr_t record=opencfw_em9305_radio_record_find_31aa64(*(volatile uint8_t *)event);
        if(record==0u)return;
        em9305_ram_805be0.u32_805c34=(uint32_t)event;
        (void)opencfw_em9305_associated_channel_state_327aac(record,*(volatile uint8_t *)(event+3u));
        return;
    }
    uintptr_t config=em9305_ram_805c5c.u32_805cac;
    uint32_t count=*(volatile uint8_t *)(config+12u);
    if(count==0u)return;
    for(uint32_t index=0u;index<count;++index){
        uintptr_t record=opencfw_em9305_radio_record_find_31aa64((uint8_t)index);
        if(record!=0u){
            (void)opencfw_em9305_memset((void *)(record+80u),0u,288u);
            count=*(volatile uint8_t *)(config+12u);
        }
    }
}
