#include <stdint.h>

/* Native 0x31a350..0x31a366: send init-state status 0xc for the current
 * command (0x805c78) with its byte +32 and words +24/+28. */
extern uint32_t opencfw_em9305_init_state_status_send_3257a4(uint32_t status, uint32_t value,
                                                             uint32_t first, uint32_t second);

uint32_t opencfw_em9305_child_31a350(void)
{
    uintptr_t command=*(volatile uint32_t *)(uintptr_t)0x805c78u;
    uint32_t second=*(volatile uint32_t *)(command+28u);
    uint32_t first=*(volatile uint32_t *)(command+24u);
    return opencfw_em9305_init_state_status_send_3257a4(0xcu,*(volatile uint8_t *)(command+32u),
                                                        first,second);
}
