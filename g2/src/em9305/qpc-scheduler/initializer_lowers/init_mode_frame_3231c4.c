#include <stdint.h>

/* Alternate source implementation for native 0x3231c4..0x323228.
 * This replaces, rather than co-links with, init_mode_event_3231c4.c.
 * Named ARC instructions retain the original twelve-byte stack frame and
 * untouched record bytes across the indirect callback and ten-byte copy. */
extern uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t context);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);
__asm__(
".text\n.balign 4\n.global opencfw_em9305_mode_event_3231c4\n"
".type opencfw_em9305_mode_event_3231c4,@function\n"
"opencfw_em9305_mode_event_3231c4:\n"
"enter_s [r13,fp,blink]\nsub_s sp,sp,0xc\n"
"ldb_s r1,[r0,0xc]\nmov_s r13,r0\ncmp r1,255\n"
"beq .Lmode3231c4_exit\n"
"mov r0,0x805c70\nld_s r2,[r0]\nstb_s r1,[sp,8]\n"
"mov r0,636\nsub r1,r13,r2\ndiv r1,r1,912\n"
"ldb r0,[r13,r0]\nstb 0,[sp,4]\nsth 6,[sp,2]\n"
"btst r0,0\nextb r0,r1\nmov r1,sp\n"
"sth r0,[r1,6]\nsth r0,[r1,0]\nbeq .Lmode3231c4_no_flag\n"
"stb 22,[sp,8]\n.Lmode3231c4_no_flag:\n"
"ld r1,[0x8028c4]\nbreq r1,0,.Lmode3231c4_event\n"
"jl [r1]\nbreq r0,0,.Lmode3231c4_event\n"
"add r13,r13,800\nmov r1,sp\nmov r2,10\n"
"bl.d opencfw_em9305_memcpy\nmov r0,r13\n"
"stb 1,[r13,-2]\n.Lmode3231c4_exit:\n"
"leave_s [r13,fp,blink,pcl]\n"
".Lmode3231c4_event:\n"
"bl.d opencfw_em9305_ll_event_callback_30e79c\nmov r0,sp\n"
"leave_s [r13,fp,blink,pcl]\n"
".size opencfw_em9305_mode_event_3231c4,.-opencfw_em9305_mode_event_3231c4\n");
