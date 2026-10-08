/* Synthetic external callback for ABI/order tests, not vendor behavior. */
#include <stdint.h>
void touch_test_init_callback(uint8_t *c){
 uint8_t *i=*(uint8_t **)(c+8);i[84]^=5u;
 ((uint32_t *)*(void **)(c+36))[17]=7u;
 register uint32_t residue __asm__("r0")=0xdeadbeefu;
 __asm__ volatile("" : "+r"(residue));
}
