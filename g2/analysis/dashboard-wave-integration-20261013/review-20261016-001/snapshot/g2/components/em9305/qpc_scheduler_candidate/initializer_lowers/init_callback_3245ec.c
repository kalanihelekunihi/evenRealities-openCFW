#include <stdint.h>

/* Native 0x3245ec..0x324626. The five-byte local header is initialized
 * in exact native store order before the 9-argument compositor call. */
extern uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t,uint32_t,
    uint32_t,uint32_t,uintptr_t,uintptr_t,uintptr_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_init_callback_3245ec(uint32_t flags,
    uintptr_t output,uintptr_t source,uint32_t count)
{
    volatile uint8_t header[5];
    header[0]=7u;
    header[4]=0u;
    header[3]=0u;
    header[2]=0u;
    header[1]=0u;
    return opencfw_em9305_radio_compose_323dc0(0u,0u,(uint8_t)flags,0u,
        (uintptr_t)header,source,output,8u,count);
}
