#include <stdint.h>

/* Native 0x32e144..0x32e162: pack two 6-byte addresses (at source and
 * source + 6) into two 64-bit words at out. Returns the length 12. */
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t address);

uint32_t opencfw_em9305_child_32e144(uintptr_t out,uintptr_t source)
{
    uint64_t first=opencfw_em9305_controller_pack_address(source);
    *(volatile uint32_t *)out=(uint32_t)first;
    *(volatile uint32_t *)(out+4u)=(uint32_t)(first>>32);
    uint64_t second=opencfw_em9305_controller_pack_address(source+6u);
    *(volatile uint32_t *)(out+8u)=(uint32_t)second;
    *(volatile uint32_t *)(out+12u)=(uint32_t)(second>>32);
    return 12u;
}
