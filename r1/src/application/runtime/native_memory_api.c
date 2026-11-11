/* Standard C memory APIs used by the Nordic BLE and formatting providers.
 * Comparison and padded copy share the existing reconstructed C algorithms. */
#include <string.h>
#include <stdint.h>
extern uint8_t *r1_native_strncpy(uint8_t *,const uint8_t *,uint32_t);
_Static_assert(sizeof(size_t)==4 && sizeof(int)==4,"R1 C library ABI");

char *strncpy(char *restrict destination,const char *restrict source,size_t length)
{
    return (char *)r1_native_strncpy((uint8_t *)destination,(const uint8_t *)source,length);
}
void *memchr(const void *source,int value,size_t length)
{
    const unsigned char *bytes=source;
    unsigned char wanted=(unsigned char)value;
    for (size_t i=0;i<length;++i)
        if (bytes[i]==wanted) return (void *)(bytes+i);
    return NULL;
}
