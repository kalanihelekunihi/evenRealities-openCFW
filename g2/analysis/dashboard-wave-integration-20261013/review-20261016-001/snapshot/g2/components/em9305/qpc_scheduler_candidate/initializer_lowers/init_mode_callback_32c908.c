#include <stdint.h>

/* Native 0x32c908..0x32c974. The BRHS.D at 0x32c94c writes the first
 * two-bit field even for index 9, then returns that low-two-bit value.
 * For indices 0..8, each of the four field masks has its own fresh
 * volatile source byte read. */
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_pal_current_time(void);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
uint32_t opencfw_em9305_mode_callback_32c908(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uint8_t mode=*(volatile uint8_t *)(context+2u);
    if (mode!=0u)
        return opencfw_em9305_receive_terminate_325c08(context,110u);
    uint8_t ready=*(volatile uint8_t *)(context+565u);
    if (ready==0u)
        return opencfw_em9305_receive_terminate_325c08(context,110u);
    uint32_t now=opencfw_em9305_pal_current_time();
    uint32_t previous=*(volatile uint32_t *)(context+232u);
    uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(now,previous);
    uint32_t limit=*(volatile uint32_t *)(context+236u);
    if (elapsed<limit) return elapsed;
    for (uint32_t index=0;index<9u;++index) {
        uintptr_t source=(uintptr_t)0x80281cu+index;
        uintptr_t target=context+193u+4u*index;
        uint8_t first=*(volatile uint8_t *)source;
        *(volatile uint8_t *)target=first&0x03u;
        uint8_t second=*(volatile uint8_t *)source;
        *(volatile uint8_t *)(target+1u)=second&0x0cu;
        uint8_t third=*(volatile uint8_t *)source;
        *(volatile uint8_t *)(target+2u)=third&0x30u;
        uint8_t fourth=*(volatile uint8_t *)source;
        *(volatile uint8_t *)(target+3u)=fourth&0xc0u;
    }
    uint8_t last=*(volatile uint8_t *)(uintptr_t)0x802825u;
    uint8_t value=last&0x03u;
    *(volatile uint8_t *)(context+229u)=value;
    return value;
}
