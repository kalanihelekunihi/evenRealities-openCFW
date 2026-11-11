#include <stdint.h>

/* Native 0x32c1d4..0x32c21c: per-event follow-up on the object's packet
 * descriptor (*(object+0x2c)+128). Kind 5: point the record's (+0x24)
 * output slot (+0x8d0) at the descriptor buffer + 352 and store bit 5 of
 * record byte 840, gated by the flag at 0x8019fd, at +0x8d5. Kind 3 with
 * a nonzero byte at +0x18: run 32c21c on the object. */
extern uint32_t opencfw_em9305_child_32c21c(uintptr_t);

void opencfw_em9305_child_32c1d4(uintptr_t object)
{
    uintptr_t descriptor=*(volatile uint32_t *)(object+0x2cu)+128u;
    uint32_t kind=*(volatile uint8_t *)(descriptor+0x14u);
    if(kind==5u) {
        uintptr_t record=*(volatile uint32_t *)(object+0x24u);
        uintptr_t buffer=*(volatile uint32_t *)descriptor;
        uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x8019fdu!=0u;
        uint32_t bit=(uint32_t)*(volatile uint8_t *)(record+840u)>>5;
        *(volatile uint32_t *)(record+0x8d0u)=buffer+352u;
        *(volatile uint8_t *)(record+0x8d5u)=(uint8_t)(bit&enabled);
        return;
    }
    if(kind==3u&&*(volatile uint8_t *)(descriptor+0x18u)!=0u)
        (void)opencfw_em9305_child_32c21c(object);
}
