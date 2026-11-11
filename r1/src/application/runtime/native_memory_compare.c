/* Shared comparison bodies: application and bootloader use one C owner. */
#include <stdint.h>
#include <string.h>
_Static_assert(sizeof(size_t)==4 && sizeof(int)==4,"R1 comparison ABI");
int32_t r1_native_memcmp(const uint8_t *a,const uint8_t *b,uint32_t length)
{
 for(uint32_t i=0;i<length;++i){int32_t difference=(int32_t)a[i]-(int32_t)b[i];if(difference)return difference;}
 return 0;
}
int memcmp(const void *a,const void *b,size_t length)
{
    return r1_native_memcmp(a,b,length);
}
