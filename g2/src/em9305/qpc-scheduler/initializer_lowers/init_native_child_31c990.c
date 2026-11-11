#include <stdint.h>

/* Native 0x31c990..0x31c9f4: for an active connection (object+0x24, byte
 * +1), insert its 912-byte schedule entry (index +88 into *0x805c70) at
 * the anchor (+24); while the insert collides, move the anchor on by
 * n * interval (+266) * 1250 us from the saved anchor and count the skipped
 * event (+262). Finally run 31c9f4 on the object. */
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_child_31c9f4(uintptr_t);

uint32_t opencfw_em9305_child_31c990(uintptr_t object)
{
    uintptr_t connection=*(volatile uint32_t *)(object+0x24u);
    if(*(volatile uint8_t *)(connection+1u)!=0u) {
        uintptr_t entry=*(volatile uint32_t *)(uintptr_t)0x805c70u+
                        *(volatile uint16_t *)(connection+88u)*912u;
        uintptr_t compare=(uintptr_t)opencfw_em9305_init_schedule_compare_318b78;
        uint32_t anchor=*(volatile uint32_t *)(entry+24u);
        uint32_t busy=opencfw_em9305_associated_schedule_insert_312da4(entry+16u,compare);
        for(uint32_t step=1u;busy==0u;++step) {
            uint32_t interval=*(volatile uint16_t *)(entry+266u);
            uint32_t offset=(uint16_t)step*interval*1250u;
            volatile uint16_t *skipped=(volatile uint16_t *)(entry+262u);
            *skipped=(uint16_t)(*skipped+1u);
            *(volatile uint32_t *)(entry+24u)=anchor+offset;
            busy=opencfw_em9305_associated_schedule_insert_312da4(entry+16u,compare);
        }
    }
    return opencfw_em9305_child_31c9f4(object);
}
