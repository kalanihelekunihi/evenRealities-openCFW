#include <stdint.h>

/* Native 0x32db54..0x32db74: pack two 6-byte addresses (at source and
 * source+6) into two 64-bit words at the destination; returns 12. */
extern uint64_t opencfw_em9305_controller_pack_address(uintptr_t);

uint32_t opencfw_em9305_dispatch_child_32db54(uintptr_t destination, uintptr_t source)
{
    volatile uint32_t *out = (volatile uint32_t *)destination;
    uint64_t first = opencfw_em9305_controller_pack_address(source);
    out[0] = (uint32_t)first;
    out[1] = (uint32_t)(first >> 32);
    uint64_t second = opencfw_em9305_controller_pack_address(source + 6u);
    out[2] = (uint32_t)second;
    out[3] = (uint32_t)(second >> 32);
    return 12u;
}
