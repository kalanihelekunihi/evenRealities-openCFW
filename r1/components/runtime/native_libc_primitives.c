#include <stdint.h>
/* Observed native state address. Initial seed/startup ownership remains a
 * separate integration gate; callers may seed this recurrence explicitly. */
static volatile uint32_t *const random_state=(volatile uint32_t *)0x20007db0u;
uint32_t r1_native_rand(void)
{
 uint32_t next=*random_state*UINT32_C(0x41c64e6d)+UINT32_C(12345);
 *random_state=next;
 return next>>1;
}
void r1_native_srand(uint32_t seed){*random_state=seed;}
/* The unsigned >= 'A' branch follows 0x28000 BCC, including malformed input.
 * Frozen pseudocode's strict comparison is not used as this contract. */
uint32_t r1_native_scanf_digit(uint32_t character,uint32_t radix)
{
 if(character<58u)character-=48u;
 uint32_t upper=character&~UINT32_C(32);
 if(upper>=65u)character=upper-55u;
 return character<radix ? character : UINT32_MAX;
}
/* Native scanner advances by a caller-supplied signed/raw word. It always
 * reads before writing the descriptor, including zero/negative advances. */
uint32_t r1_native_scanf_format_getc(uint32_t *cursor,uint32_t advance)
{
 uint32_t current=*cursor;
 uint32_t result=*(const volatile uint8_t *)(uintptr_t)current;
 *cursor=current+advance;
 return result;
}
