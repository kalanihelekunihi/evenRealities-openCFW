#include <stdint.h>

/* Native 0x32a5ac..0x32a5f2: classify a packet against the context at
 * 0x802810 with natives 0x3191dc and 0x319714 and pass the result code to
 * native 0x32a000: 12 when either check fails, 14 when either returns 0x1e,
 * otherwise 13. Inactive packets (byte 0 clear) return 0. */
extern uint32_t opencfw_em9305_child_3191dc(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_319714(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_32a000(uint32_t,uint32_t);

uint32_t opencfw_em9305_callback_32a5ac(uintptr_t packet, uint32_t argument)
{
    uint32_t code;
    if (*(volatile uint8_t *)packet == 0u) return 0u;
    uint32_t first = opencfw_em9305_child_3191dc(0x802810u, argument,
                                                 *(volatile uint8_t *)(packet + 2u));
    if (first == 0u) {
        code = 12u;
    } else {
        uint32_t second = opencfw_em9305_child_319714(0x802810u, argument,
                                                      *(volatile uint8_t *)(packet + 2u));
        if (second == 0u) code = 12u;
        else if (first == 0x1eu || second == 0x1eu) code = 14u;
        else code = 13u;
    }
    return opencfw_em9305_child_32a000((uint32_t)packet, code);
}
