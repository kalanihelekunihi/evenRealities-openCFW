#include <stdint.h>
/* Complete native guard303f80..3f8a and quantizer312c5c..c9e.
 * Named ISA preserves caller-observed registers and original DSP flags. */
extern uint32_t opencfw_em9305_auxiliary_guard_interval(void);
extern uint32_t opencfw_em9305_channel_timing_adjust_312c5c(uint32_t);
__asm__(
".section .text.opencfw_em9305_auxiliary_guard_interval,\"ax\",@progbits\n"
".align 2\n"
".global opencfw_em9305_auxiliary_guard_interval\n"
".type opencfw_em9305_auxiliary_guard_interval,@function\n"
"opencfw_em9305_auxiliary_guard_interval:\n"
"mov_s r0,0x805c18\n"
"ld r0,[r0,0]\n"
"j_s.d [blink]\n"
"ldh_s r0,[r0,6]\n"
".size opencfw_em9305_auxiliary_guard_interval,.-opencfw_em9305_auxiliary_guard_interval\n"
);
__asm__(
".section .text.opencfw_em9305_channel_timing_adjust_312c5c,\"ax\",@progbits\n"
".align 2\n"
".global opencfw_em9305_channel_timing_adjust_312c5c\n"
".type opencfw_em9305_channel_timing_adjust_312c5c,@function\n"
"opencfw_em9305_channel_timing_adjust_312c5c:\n"
"mov_s r2,r0\n"
"brhs r0,0x3bfc4,1f\n"
"mpymu r0,r0,0x11111112\n"
"lsr_s r0,r0\n"
"mpyuw r0,r0,30\n"
"cmp_s r0,r2\n"
"jnc [blink]\n"
"j_s.d [blink]\n"
"add r0,r0,30\n"
"1: mpymu r0,r0,0x69d0369e\n"
"add1 r1,r2,r2\n"
"mov r3,300\n"
"add_s r1,r1,r0\n"
"lsr_s r1,r1,10\n"
"mpywhul r0,r3,r1\n"
"cmp_s r0,r2\n"
"jnc [blink]\n"
"j_s.d [blink]\n"
"add_s r0,r0,r3\n"
".size opencfw_em9305_channel_timing_adjust_312c5c,.-opencfw_em9305_channel_timing_adjust_312c5c\n"
);
