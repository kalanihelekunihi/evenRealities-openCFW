#include <stdint.h>

/* Native 0x32cde0..0x32ce02. BRNE.D at 0x32cdf4 stores ctx+552 on
 * both branches. 0x317ea4 remains a genuine child until independently
 * attributed; this complete parent does not supply a placeholder. */
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t);
uint32_t opencfw_em9305_mode_callback_32cde0(uintptr_t context,
                                               uintptr_t callback_code)
{
    (void)callback_code;
    uint8_t mode=*(volatile uint8_t *)(context+2u);
    uint8_t value=*(volatile uint8_t *)(uintptr_t)0x80281cu;
    *(volatile uint8_t *)(context+552u)=value;
    if (mode!=1u)
        return value;
    uint32_t result=opencfw_em9305_mode_callback_child_317ea4(value);
    *(volatile uint16_t *)(context+200u)=(uint16_t)result;
    return result;
}
