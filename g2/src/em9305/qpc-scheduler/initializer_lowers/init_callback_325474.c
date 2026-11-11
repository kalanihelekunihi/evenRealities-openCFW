#include <stdint.h>

/* Native 0x325474..0x32553e. The 168-byte local frame is reserved by the
 * entry function below; mode 3 leaves most frame bytes untouched before the
 * event callback. The two key-operation children remain genuine source imports. */
extern uint32_t opencfw_em9305_radio_key_operation_30ff70(uintptr_t,
                                                             uintptr_t,
                                                             uintptr_t);
extern uint32_t opencfw_em9305_radio_key_operation_30ffbc(uintptr_t,
                                                             uintptr_t);
extern uint32_t opencfw_em9305_radio_random_bytes_310038(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_callback_child_322e44(uintptr_t);
extern uint32_t opencfw_em9305_ll_vendor_validate_32e328(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);

uint32_t opencfw_em9305_init_callback_body_325474(uintptr_t frame)
{
    uint32_t mode=*(volatile uint8_t *)(uintptr_t)0x805258u;
    if(mode==1u) {
        uint32_t ready=*(volatile uint8_t *)(uintptr_t)0x805b81u;
        if(ready==0u) {
            (void)opencfw_em9305_radio_random_bytes_310038(frame+72u,32u);
            for(uint32_t index=0u;index<32u;++index)
                *(volatile uint8_t *)(uintptr_t)(0x805b60u+index)=
                    *(volatile uint8_t *)(frame+103u-index);
        }
        (void)opencfw_em9305_radio_key_operation_30ffbc(0x805b60u,
                                                           frame+104u);
        (void)opencfw_em9305_memset((void *)frame,0u,70u);
        *(volatile uint8_t *)(frame+2u)=19u;
        (void)opencfw_em9305_memcpy((void *)(frame+5u),
                                    (const void *)(frame+104u),32u);
        (void)opencfw_em9305_memcpy((void *)(frame+37u),
                                    (const void *)(frame+136u),32u);
        (void)opencfw_em9305_ll_event_callback_30e79c(frame);
        *(volatile uint8_t *)(uintptr_t)0x805b80u=0u;
        *(volatile uint8_t *)(uintptr_t)0x805258u=0u;
    } else if(mode==2u) {
        (void)opencfw_em9305_radio_key_operation_30ff70(0x80527cu,
                                                           0x80525cu,frame);
        (void)opencfw_em9305_callback_child_322e44(frame);
        *(volatile uint8_t *)(uintptr_t)0x805258u=0u;
        *(volatile uint8_t *)(uintptr_t)0x805b80u=0u;
    } else if(mode==3u) {
        uint32_t result=opencfw_em9305_ll_vendor_validate_32e328(0x80527cu,0u);
        *(volatile uint8_t *)(frame+4u)=(uint8_t)result;
        *(volatile uint32_t *)frame=1u<<22;
        (void)opencfw_em9305_ll_event_callback_30e79c(frame);
        *(volatile uint8_t *)(uintptr_t)0x805b80u=0u;
        *(volatile uint8_t *)(uintptr_t)0x805258u=0u;
    }
    return 0u;
}

/* Native entry 0x325474: reserve the 168-byte local frame and run the body
 * on it (stock: enter_s, sub sp,sp,168, mov r0,sp). The body leaves most
 * bytes untouched in mode 3; they stay uninitialised, as in stock. */
uint32_t opencfw_em9305_init_callback_325474(void)
{
    uint32_t frame[42];
    return opencfw_em9305_init_callback_body_325474((uintptr_t)frame);
}
