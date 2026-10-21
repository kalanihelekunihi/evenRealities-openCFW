/* Internal IAR helper contracts, not generic memcpy return semantics.
 * Fill41560c accepts out,count,value. Copy4156ac is the aligned helper;
 * its final byte does not advance rawR0. Nonoverlapping aligned inputs only. */
#include <stdint.h>
void *opencfw_iar_fill_native(void *out,uint32_t count,uint32_t value){
 uint8_t *p=out;for(uint32_t i=0;i<count;i++)p[i]=(uint8_t)value;return out;
}
void *opencfw_iar_aligned_copy_native(void *out,const void *in,uint32_t count){
 uint8_t *p=out;const uint8_t *s=in;for(uint32_t i=0;i<count;i++)p[i]=s[i];
 return p+(count&~1u);
}
