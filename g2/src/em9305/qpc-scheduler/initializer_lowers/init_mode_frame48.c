#include <stdint.h>

/* Mutually exclusive source alternative to init_mode_event_323028.c.
 * This native-frame ARC wrapper preserves all six incoming caller-stack
 * words, the 0x30-byte local frame, and untouched record bytes. It uses
 * relocations to selected C memset/address-writer/LL-callback providers. */
extern uint32_t opencfw_em9305_mode_event_323028(
    uint32_t,uint32_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
__asm__(
".text\n.balign 4\n.global opencfw_em9305_mode_event_323028\n"
".type opencfw_em9305_mode_event_323028,@function\n"
"opencfw_em9305_mode_event_323028:\n"
"enter_s [r13-r21,fp,blink]\nsub_s sp,sp,0x30\n"
"ld_s r14,[sp,0x64]\nmov_s r13,r2\nmov_s r15,r0\n"
"stb_s r1,[sp,8]\nsth r0,[sp,6]\nsth r0,[sp]\n"
"add r0,sp,10\nmov r1,0\nmov r2,25\n"
"mov r18,r7\nmov r19,r6\nmov r20,r5\nmov r21,r4\n"
"stb r3,[sp,9]\nstb 5,[sp,2]\nstb_s r14,[sp,4]\n"
"bl.d opencfw_em9305_memset\nstb r14,[sp,3]\n"
"ld_s r1,[sp,0x70]\nld_s r0,[sp,0x6c]\n"
"ld r16,[sp,96]\nld r17,[sp,92]\n"
"sth r1,[sp,36]\nstb r0,[sp,35]\n"
"breq_s r13,0,.Lmode323028_addresses\n"
"ld_s r2,[r13,0x20]\nldh_s r1,[r13,0x24]\n"
"ldb r0,[r13,43]\nst_s r2,[sp,16]\n"
"sth r1,[sp,20]\nstb r0,[sp,22]\n"
".Lmode323028_addresses:\n"
"add r0,sp,10\nmov_s r1,r21\n"
"bl.d opencfw_em9305_radio_address_write_3045e8\nmov_s r2,r20\n"
"add r0,sp,29\nmov_s r1,r19\n"
"bl.d opencfw_em9305_radio_address_write_3045e8\nmov_s r2,r18\n"
"add r0,sp,23\nmov_s r1,r17\n"
"bl.d opencfw_em9305_radio_address_write_3045e8\nmov_s r2,r16\n"
"bl.d opencfw_em9305_ll_event_callback_30e79c\nmov_s r0,sp\n"
"breq_s r14,0,.Lmode323028_flag\n"
".Lmode323028_return:\nleave_s [r13-r21,fp,blink,pcl]\n"
".Lmode323028_flag:\n"
"mov r0,0x805a95\nldb_s r0,[r0]\n"
"bbit0.d.t r0,6,.Lmode323028_return\nmov r0,33\n"
"ld_s r1,[sp,0x68]\nmov_s r2,sp\n"
"sth_s r0,[r2,42]\nadd r0,sp,40\n"
"sth_s r15,[r2,44]\nsth_s r15,[r2,40]\n"
"bl.d opencfw_em9305_ll_event_callback_30e79c\nstb r1,[sp,46]\n"
"leave_s [r13-r21,fp,blink,pcl]\n"
".size opencfw_em9305_mode_event_323028,.-opencfw_em9305_mode_event_323028\n");
