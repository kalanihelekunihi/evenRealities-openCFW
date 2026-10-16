#include <stdint.h>
/* Full native322178..322180: preserves incoming R2/other live registers and
 * tail-return linkage; writes record flag in branch delay before child. */
extern uint32_t opencfw_em9305_callback_322178(uintptr_t);
extern uint32_t opencfw_em9305_callback_32233c(uintptr_t,uintptr_t,uint32_t);
__asm__(
".text\n.align 2\n.global opencfw_em9305_callback_322178\n"
".type opencfw_em9305_callback_322178,@function\n"
"opencfw_em9305_callback_322178:\n"
"ld r1,[r0,36]\n"
"b.d opencfw_em9305_callback_32233c\n"
"stb 1,[r1,8]\n"
".size opencfw_em9305_callback_322178,.-opencfw_em9305_callback_322178\n");
