#include <stdint.h>

/* Native 0x3232a8..0x3232da. The -16 ARC frame preserves the untouched
 * callback packet bytes; it is not an initialized C structure. */
extern uint32_t opencfw_em9305_mode_event_3232a8(uintptr_t context,
                                                     uint32_t reason);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
__asm__(
".text\n.balign 4\n.global opencfw_em9305_mode_event_3232a8\n"
".type opencfw_em9305_mode_event_3232a8,@function\n"
"opencfw_em9305_mode_event_3232a8:\n"
"st.aw blink,[sp,-16]\n"
"mov r2,0x805c70\nld_s r2,[r2]\n"
"stb_s r1,[sp,8]\nmov r1,552\n"
"sub r2,r0,r2\ndiv r2,r2,912\n"
"ldb_s r0,[r0,r1]\nmov r1,46\nmov r3,sp\n"
"sth_s r1,[r3,6]\nstb_s r0,[sp,12]\n"
"extb r0,r2\nsth_s r0,[r3,10]\nsth_s r0,[r3,4]\n"
"bl.d opencfw_em9305_ll_event_callback_30e79c\nadd r0,sp,4\n"
"ld.ab blink,[sp,16]\nj [blink]\n"
".size opencfw_em9305_mode_event_3232a8,.-opencfw_em9305_mode_event_3232a8\n");
