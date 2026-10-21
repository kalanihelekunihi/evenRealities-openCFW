#include <stdint.h>

/* Mutually exclusive source alternative to init_mode_event_323374.c.
 * Named ARC instructions preserve the native -20 SP frame and ambient
 * bytes forwarded to the selected event callback. */
extern uint32_t opencfw_em9305_mode_event_323374(uintptr_t context);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
__asm__(
".text\n.balign 4\n.global opencfw_em9305_mode_event_323374\n"
".type opencfw_em9305_mode_event_323374,@function\n"
"opencfw_em9305_mode_event_323374:\n"
"st.aw blink,[sp,-20]\n"
"mov r1,0x805c70\nld_s r1,[r1]\n"
"stb 0,[sp,8]\nsth 9,[sp,6]\n"
"sub r1,r0,r1\ndiv r1,r1,912\n"
"add r0,r0,528\nldb_s r3,[r0]\n"
"ldh_s r2,[r0,2]\nldh_s r0,[r0,4]\n"
"stb_s r3,[sp,12]\nmov r12,sp\n"
"sth_s r2,[r12,14]\nsth_s r0,[r12,16]\n"
"extb r0,r1\nsth_s r0,[r12,10]\nsth_s r0,[r12,4]\n"
"bl.d opencfw_em9305_ll_event_callback_30e79c\nadd r0,sp,4\n"
"ld.ab blink,[sp,20]\nj [blink]\n"
".size opencfw_em9305_mode_event_323374,.-opencfw_em9305_mode_event_323374\n");
