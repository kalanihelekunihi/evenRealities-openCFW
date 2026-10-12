#include <stdint.h>

/* Native 0x323314..0x323370. The -20 ARC frame is passed, including
 * untouched bytes, to the selected event callback. */
extern uint32_t opencfw_em9305_mode_event_323314(uintptr_t context,
                                                     uint32_t reason);
extern uint32_t opencfw_em9305_primary_query_313960(uintptr_t packet,
                                                   uint32_t first,
                                                   uint32_t second);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
__asm__(
".text\n.balign 4\n.global opencfw_em9305_mode_event_323314\n"
".type opencfw_em9305_mode_event_323314,@function\n"
"opencfw_em9305_mode_event_323314:\n"
"st.aw blink,[sp,-20]\n"
"ld r2,[0x805c70]\nld r12,[0x805cac]\n"
"st 0,[sp,16]\nsub r2,r0,r2\ndiv r2,r2,912\n"
"st 0,[sp,12]\nstb_s r1,[sp,8]\nstb r1,[sp,7]\n"
"stb 10,[sp,6]\nextb r3,r2\nmov r1,sp\n"
"sth_s r3,[r1,10]\nldb_s r2,[r12,4]\n"
"brhs.d r2,9,.Lmode_323314_high\n"
"sth_s r3,[r1,4]\n"
"ld r2,[r0,548]\nld r1,[r0,544]\n"
"b .Lmode_323314_call\n"
".Lmode_323314_high:\n"
"ld r2,[r0,540]\nld r1,[r0,536]\n"
".Lmode_323314_call:\n"
"bl.d opencfw_em9305_primary_query_313960\nadd r0,sp,12\n"
"bl.d opencfw_em9305_ll_event_callback_30e79c\nadd r0,sp,4\n"
"ld.ab blink,[sp,20]\nj [blink]\n"
".size opencfw_em9305_mode_event_323314,.-opencfw_em9305_mode_event_323314\n");
