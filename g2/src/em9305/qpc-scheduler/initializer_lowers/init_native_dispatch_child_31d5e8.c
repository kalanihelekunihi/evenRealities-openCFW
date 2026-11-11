#include <stdint.h>

/* Native 0x31d5e8..0x31d6a4: prepare a receive buffer (allocated when none
 * is given; 0 if that fails) for the record: notify the hook at *0x8052cc
 * with the pending pair at 0x802a2c when the record is encrypted (+484),
 * set up the buffer for the received length (+4, plus 4 for the MIC) at
 * the anchor time, choose the next channel (from the stream selected by
 * 0x8029ac when it is below the stream count +52, else the record's
 * channel +409) into 0x802a28, and unless a pending flag (0x8029b2) is
 * set without a buffer, restart the timer from the doubled secondary
 * time. Returns 1. */
extern uintptr_t opencfw_em9305_ll_receive_buffer_allocate_3175f0(void);
extern uint32_t opencfw_em9305_dispatch_child_302f00(uintptr_t,uint32_t,uint32_t,uint32_t,
                                                     uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_30e6b0(uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_302f70(uint32_t);

uint32_t opencfw_em9305_dispatch_child_31d5e8(uintptr_t record,uint32_t given,uintptr_t buffer)
{
    if(buffer==0u) {
        buffer=opencfw_em9305_ll_receive_buffer_allocate_3175f0();
        if(buffer==0u) return 0u;
    }
    uint32_t encrypted=*(volatile uint8_t *)(record+484u);
    if(encrypted!=0u) {
        uintptr_t hook=*(volatile uint32_t *)(uintptr_t)0x8052ccu;
        if(hook!=0u) {
            ((void (*)(uint32_t,uint32_t))hook)(*(volatile uint32_t *)(uintptr_t)0x802a2cu,
                                                *(volatile uint32_t *)(uintptr_t)0x802a30u);
            encrypted=*(volatile uint8_t *)(record+484u);
        }
    }
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)0x8029acu;
    uint32_t anchor=*(volatile uint32_t *)(record+252u)+*(volatile uint32_t *)(record+264u);
    uint32_t length=*(volatile uint16_t *)(record+4u)+((encrypted!=0u)?4u:0u)+2u;
    (void)opencfw_em9305_dispatch_child_302f00(buffer,(uint16_t)length,
        *(volatile uint32_t *)(state+0xcu)+anchor,*(volatile uint32_t *)(state+0x10u),given);
    uint32_t stream=state[0];
    volatile uint8_t *channel=(volatile uint8_t *)(uintptr_t)0x802a28u;
    if(stream>=*(volatile uint8_t *)(record+52u)) {
        *channel=*(volatile uint8_t *)(record+409u);
    } else {
        uintptr_t object=*(volatile uint32_t *)(record+0x38u+stream*4u);
        if(object!=0u&&*(volatile uint8_t *)object!=0u) {
            uintptr_t selector=object+120u;
            *channel=*(volatile uint8_t *)(selector+57u);
            *(volatile uint8_t *)(selector+57u)=
                (uint8_t)opencfw_em9305_dispatch_child_30e6b0(selector);
        }
    }
    if(state[6]!=0u&&given==0u) return 1u;
    uint32_t time=opencfw_em9305_init_secondary_time_317ebc(*(volatile uint32_t *)(state+0xcu),
        *(volatile uint16_t *)(record+244u));
    *(volatile uint32_t *)(record+172u)=time<<1;
    (void)opencfw_em9305_dispatch_child_302f70(time<<1);
    return 1u;
}
