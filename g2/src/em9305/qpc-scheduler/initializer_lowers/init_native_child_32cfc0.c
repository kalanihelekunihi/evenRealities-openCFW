#include <stdint.h>

/* Native 0x32cfc0..0x32cfe8: copy the 8-byte block at 0x80281c to record+429
 * and the following 4 bytes (0x802824) to record+441. */
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);

uintptr_t opencfw_em9305_child_32cfc0(uintptr_t record)
{
    (void)opencfw_em9305_memcpy((void *)(record+429u),(const void *)(uintptr_t)0x80281cu,8u);
    return (uintptr_t)opencfw_em9305_memcpy((void *)(record+441u),
                                            (const void *)(uintptr_t)0x802824u,4u);
}
