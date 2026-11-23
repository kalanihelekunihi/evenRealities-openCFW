#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x318f2c..0x318fc0: collect and clear each active connection's
 * pending-terminate byte (+376) under a critical section, then for each
 * connection (highest first) pass a non-zero byte with the handle to the
 * host callback at ((uintptr_t)&em9305_ram_805af0 + 0x20u) and terminate reception (reason 0x3e) when
 * the connection has its close flag (+404) set and an empty queue (+360).
 * The connection count is the configuration byte (*((uintptr_t)&em9305_ram_805c5c + 0x50u))+34; stock
 * keeps the bytes in one zeroed word and requires 1..4 connections. */
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);
extern uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t queue);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t source,
                                                        uint32_t reason);
typedef void (*opencfw_em9305_terminate_callback_t)(uint32_t handle,uint32_t reason);

void opencfw_em9305_callback_318f2c(void)
{
    _Alignas(4) uint8_t pending[4]={0u,0u,0u,0u};
    uintptr_t config=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x50u);
    uint32_t count=*(volatile uint8_t *)(config+34u);
    (void)opencfw_em9305_wsf_critical_enter();
    uintptr_t base=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x14u);
    for(uint32_t index=count;index!=0u;--index){
        uintptr_t connection=base+(index-1u)*912u;
        if(*(volatile uint8_t *)connection==0u)continue;
        uint32_t reason=*(volatile uint8_t *)(connection+376u);
        *(volatile uint8_t *)(connection+376u)=0u;
        pending[index-1u]=(uint8_t)reason;
    }
    (void)opencfw_em9305_wsf_critical_exit();
    uint32_t index=*(volatile uint8_t *)(*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x50u)+34u);
    do{
        uint32_t reason=pending[index-1u];
        --index;
        if(reason!=0u){
            uintptr_t callback=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805af0 + 0x20u);
            if(callback!=0u)
                ((opencfw_em9305_terminate_callback_t)callback)((uint16_t)index,reason);
        }
        uintptr_t connection=base+index*912u;
        if(*(volatile uint8_t *)(connection+404u)!=0u
           &&opencfw_em9305_wsf_queue_empty(connection+360u)!=0u)
            (void)opencfw_em9305_receive_terminate_325c08(connection,0x3eu);
    }while(index!=0u);
}
