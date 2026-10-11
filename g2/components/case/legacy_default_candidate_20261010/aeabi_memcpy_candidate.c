/* SPDX-License-Identifier: MIT
 * Freestanding ARM EABI byte-copy helper required by generated candidate C.
 * The compiler calls this only for nonoverlapping object copies.
 */
#include <stddef.h>
#include <stdint.h>

void __aeabi_memcpy(void *destination,const void *source,size_t length)
{
    uint8_t *to=(uint8_t *)destination;
    const uint8_t *from=(const uint8_t *)source;
    for(size_t i=0;i<length;++i) to[i]=from[i];
}
