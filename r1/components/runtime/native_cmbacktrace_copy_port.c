#include <stdint.h>
extern uint8_t *r1_native_strncpy(uint8_t *,const uint8_t *,uint32_t);
/* Character-pointer adaptation only; the already verified native byte-copy
 * provider supplies truncation and padding behavior without another clone. */
char *r1_cmb_copy_name(char *destination,const char *source,uint32_t count)
{
 return (char *)r1_native_strncpy((uint8_t *)destination,(const uint8_t *)source,count);
}
