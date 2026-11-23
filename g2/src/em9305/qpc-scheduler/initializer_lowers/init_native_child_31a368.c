#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31a368..0x31a3ea: extended-initiator stop. For each of the
 * three initiator records whose bit is set in the pending mask (((uintptr_t)&em9305_ram_802a2c + 0x32u))
 * but not in the done mask (((uintptr_t)&em9305_ram_802a2c + 0x31u)), terminate its connection (record
 * +88 indexes the 912-byte table at *((uintptr_t)&em9305_ram_805c5c + 0x14u)) with reason 0x4d if that
 * connection is active. Then run 31ff2c on the command and, unless the
 * command state is 3, report the fixed six-byte event (0x334452) and send
 * status 2 with the id byte and words at ((uintptr_t)&em9305_ram_802a2c + 0x30u)/((uintptr_t)&em9305_ram_802a2c + 0x28u)/((uintptr_t)&em9305_ram_802a2c + 0x2cu). */
extern uint8_t *const opencfw_em9305_ext_init_records_3357a8[3];
extern const uint16_t opencfw_em9305_ext_init_event_334452[3];
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,
                                                        uint32_t reason);
extern uint32_t opencfw_em9305_child_31ff2c(uintptr_t command);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
extern uint32_t opencfw_em9305_init_state_status_send_3257a4(uint32_t code,
    uint32_t id,uint32_t low,uint32_t high);

void opencfw_em9305_child_31a368(uintptr_t command)
{
    uint32_t pending=*(volatile uint8_t *)((uintptr_t)&em9305_ram_802a2c + 0x32u);
    for(uint32_t index=0u;index<3u;++index){
        uint32_t bit=1u<<index;
        if((pending&bit)==0u)continue;
        if((*(volatile uint8_t *)((uintptr_t)&em9305_ram_802a2c + 0x31u)&bit)!=0u)continue;
        uintptr_t record=(uintptr_t)opencfw_em9305_ext_init_records_3357a8[index];
        uintptr_t base=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x14u);
        uintptr_t connection=*(volatile uint16_t *)(record+88u)*912u+base;
        if(*(volatile uint8_t *)connection==0u)continue;
        (void)opencfw_em9305_receive_terminate_325c08(connection,0x4du);
        pending=*(volatile uint8_t *)((uintptr_t)&em9305_ram_802a2c + 0x32u);
    }
    (void)opencfw_em9305_child_31ff2c(command);
    if(*(volatile uint8_t *)command==3u)return;
    _Alignas(4) uint16_t event[3];
    event[0]=opencfw_em9305_ext_init_event_334452[0];
    event[1]=opencfw_em9305_ext_init_event_334452[1];
    event[2]=opencfw_em9305_ext_init_event_334452[2];
    (void)opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
    (void)opencfw_em9305_init_state_status_send_3257a4(2u,
        *(volatile uint8_t *)((uintptr_t)&em9305_ram_802a2c + 0x30u),*(volatile uint32_t *)((uintptr_t)&em9305_ram_802a2c + 0x28u),
        *(volatile uint32_t *)((uintptr_t)&em9305_ram_802a2c + 0x2cu));
}
