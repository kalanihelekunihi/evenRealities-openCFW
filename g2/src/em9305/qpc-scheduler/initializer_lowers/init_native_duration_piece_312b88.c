#include <stdint.h>
/* Full native312b88..312bb2. Preserve native R1 result and R2/R3..R12
 * scratch values consumed by connected original callers. Named ISA source,
 * not encoded stock bytes. No stack frame or child calls. */
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t,uint32_t,uint32_t);
__asm__(
".text\n.align 2\n.global opencfw_em9305_radio_duration_piece_312b88\n"
".type opencfw_em9305_radio_duration_piece_312b88,@function\n"
"opencfw_em9305_radio_duration_piece_312b88:\n"
"breq r0,2,1f\n"
"brne.d r0,3,2f\n"
"cmp_s r1,1\n"
"mov_s r1,8\n"
"mov_s r0,27\n"
"mov.eq r1,2\n"
"add3_s r0,r0,r2\n"
"mpywhl r0,r0,r1\n"
"j_s.d [blink]\n"
"add3 r0,r0,47\n"
"1: mov_s r0,36\n"
"j_s.d [blink]\n"
"add2_s r0,r0,r2\n"
"2: asl_s r0,r2,3\n"
"j_s.d [blink]\n"
"add1 r0,r0,32\n"
".size opencfw_em9305_radio_duration_piece_312b88,.-opencfw_em9305_radio_duration_piece_312b88\n");
