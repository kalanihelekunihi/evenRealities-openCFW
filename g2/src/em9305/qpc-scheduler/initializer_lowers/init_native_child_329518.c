#include <stdint.h>

/* Native 0x329518..0x329534: true when the record's byte at +635 is 0x11
 * and its byte at +623 is 2. */
uint32_t opencfw_em9305_child_329518(uintptr_t record)
{
    if(*(volatile uint8_t *)(record+635u)!=0x11u) return 0u;
    if(*(volatile uint8_t *)(record+623u)!=2u) return 0u;
    return 1u;
}
