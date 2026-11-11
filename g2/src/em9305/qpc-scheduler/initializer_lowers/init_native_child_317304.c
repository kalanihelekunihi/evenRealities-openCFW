#include <stdint.h>

/* Native 0x317304..0x317320: decrement the 7-bit reference count of the
 * record's attached object (+184) and release it when it reaches zero. */
extern void opencfw_em9305_child_317320(uintptr_t record);

void opencfw_em9305_child_317304(uintptr_t record)
{
    uintptr_t object=*(volatile uint32_t *)(record+184u);
    if(object==0u)return;
    uint32_t count=(*(volatile uint8_t *)(object+4u)&0x7fu)-1u;
    *(volatile uint8_t *)(object+4u)=(uint8_t)count;
    if(count==0u)opencfw_em9305_child_317320(record);
}
