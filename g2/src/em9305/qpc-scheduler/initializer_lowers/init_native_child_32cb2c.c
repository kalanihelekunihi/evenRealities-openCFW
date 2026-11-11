#include <stdint.h>

/* Native 0x32cb2c..0x32cb40: copy the 16-byte block at offset 4 of the
 * shared record at 0x805c6c into record+405. */
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t length);

void *opencfw_em9305_child_32cb2c(uintptr_t record)
{
    uintptr_t shared=*(volatile uint32_t *)0x805c6cu;
    return opencfw_em9305_memcpy((void *)(record+405u),(const void *)(shared+4u),16u);
}
