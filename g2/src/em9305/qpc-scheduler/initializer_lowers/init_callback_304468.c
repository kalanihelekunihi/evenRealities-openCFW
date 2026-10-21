#include <stdint.h>

/* Native 0x304468..0x3044e4. The 5th argument is the live ARC R4 word
 * loaded from context+168. Both dynamic callback slots are read from the
 * context, and the radio-cancel path occurs before the first callback. */
extern uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t);

uint32_t opencfw_em9305_init_callback_304468(uintptr_t request,
                                               uintptr_t context)
{
    uintptr_t mode_pointer=*(volatile uint32_t *)(context+104u);
    uintptr_t fields=context+168u;
    uintptr_t callback=*(volatile uint32_t *)(fields+64u);
    uint32_t mode=*(volatile uint8_t *)mode_pointer&15u;
    if(callback==0u)return 1u;
    if(mode==7u) {
        uintptr_t payload=*(volatile uint32_t *)(request+44u);
        uint32_t kind=*(volatile uint8_t *)payload;
        if(kind!=8u)return 1u;
        uint32_t enabled=*(volatile uint8_t *)(fields+60u);
        if(enabled==0u)return 1u;
        (void)opencfw_em9305_radio_cancel_30fab8(enabled);
        uint32_t index=*(volatile uint8_t *)(context+225u);
        uint32_t r4=*(volatile uint32_t *)fields;
        uint32_t r3=*(volatile uint32_t *)(fields+84u);
        uint32_t r2=*(volatile uint32_t *)(fields+76u);
        uint32_t r1=*(volatile uint32_t *)(fields+68u);
        uintptr_t current_callback=*(volatile uint32_t *)(fields+64u);
        (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t))current_callback)
            (context+index*4u+208u,r1,r2,r3,r4);
        uintptr_t flag=context+261u;
        if(*(volatile uint8_t *)flag==1u)*(volatile uint8_t *)flag=2u;
        return 0u;
    }
    if(mode==5u) {
        uintptr_t payload=*(volatile uint32_t *)(request+44u);
        uint32_t kind=*(volatile uint8_t *)payload;
        if(kind!=8u)return 1u;
        uint32_t r4=*(volatile uint32_t *)fields;
        (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t))callback)
            (context+208u,0u,0u,0u,r4);
        return 0u;
    }
    return 1u;
}
