#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32bb9c..0x32bc6a: connection-complete callback for a create
 * command. With a free connection entry, seed it from the command (PHY
 * +52 -> +524, channel/handle +84/+86 -> +890/+892, timing +60/+64 ->
 * +516/+520), make the command current and start it (32a000, event 0xb);
 * otherwise report mode event 9 with the command's parameters. A command
 * with no peer (+84 = 0xff, +86 = 0xffff) releases common resource 1 and,
 * when +55 is set, reports LL event 0x1c for the entry index. */
extern uintptr_t opencfw_em9305_init_connection_allocate_316c58(void);
extern uint32_t opencfw_em9305_child_32a000(uintptr_t entry, uint32_t code);
extern uint32_t opencfw_em9305_mode_event_323028(uint32_t, uint32_t, uintptr_t, uint32_t,
                                                 uint32_t, uint32_t, uint32_t, uint32_t,
                                                 uint32_t, uint32_t, uint32_t, uint32_t,
                                                 uint32_t, uint32_t);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t resource);
extern uint32_t opencfw_em9305_dispatch_child_30e774(uint32_t handle, uint32_t status,
                                                     uint32_t value, uint32_t extra);

void opencfw_em9305_callback_32bb9c(uintptr_t command)
{
    uintptr_t entry=opencfw_em9305_init_connection_allocate_316c58();
    if(entry!=0u){
        uint32_t phy=*(volatile uint8_t *)(command+52u);
        uint32_t channel=*(volatile uint8_t *)(command+84u);
        uint32_t handle=*(volatile uint16_t *)(command+86u);
        uint32_t second=*(volatile uint32_t *)(command+64u);
        uint32_t first=*(volatile uint32_t *)(command+60u);
        *(volatile uint8_t *)(entry+524u)=(uint8_t)phy;
        *(volatile uint8_t *)(entry+890u)=(uint8_t)channel;
        *(volatile uint16_t *)(entry+892u)=(uint16_t)handle;
        *(volatile uint8_t *)(entry+2u)=1u;
        em9305_ram_805c5c.u32_805c6c=(uint32_t)command;
        *(volatile uint32_t *)(entry+520u)=second;
        *(volatile uint32_t *)(entry+516u)=first;
        (void)opencfw_em9305_child_32a000(entry,0xbu);
    }else{
        (void)opencfw_em9305_mode_event_323028(0u,1u,command+4u,
            *(volatile uint8_t *)(command+52u),
            *(volatile uint32_t *)(command+60u),*(volatile uint32_t *)(command+64u),
            *(volatile uint32_t *)(command+68u),*(volatile uint32_t *)(command+72u),
            *(volatile uint32_t *)(command+76u),*(volatile uint32_t *)(command+80u),
            9u,0u,*(volatile uint8_t *)(command+84u),*(volatile uint16_t *)(command+86u));
    }
    if(*(volatile uint8_t *)(command+84u)!=255u)return;
    if(*(volatile uint16_t *)(command+86u)!=0xffffu)return;
    (void)opencfw_em9305_common_release_304588(1u);
    if(*(volatile uint8_t *)(command+55u)==0u)return;
    uintptr_t base=em9305_ram_805c5c.u32_805c70;
    uint32_t status=*(volatile uint8_t *)(command+56u);
    uint32_t index=(uint8_t)((int32_t)(entry-base)/912);
    (void)opencfw_em9305_dispatch_child_30e774(*(volatile uint8_t *)command,0u,index,status);
}
