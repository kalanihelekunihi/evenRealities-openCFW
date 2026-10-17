#include <stdint.h>
/* Native FlashDB adapter: preserves saved argument words, logging and native
 * uninitialized return 0 (upstream 2.0.0 instead returns FDB_INIT_FAILED).
 * Provider bodies remain explicit imports. No opcode arrays. */
__attribute__((naked,section(".text.r1_fdb_native_query_count")))
void r1_health_sync_provider_00063cb4(void) {
 __asm__ volatile(
 "push {r1,r2,r3,r4,r5,lr}\n"
 "mov r4,r0\nmovs r0,#0\nstr r0,[sp,#4]\nstr r0,[sp,#8]\nstrb.w r3,[sp,#4]\n"
 "ldrb r0,[r4,#24]\ncbz r0,1f\nadd r0,sp,#4\nstr r0,[sp]\nldr r3,3f\nmov r0,r4\n"
 "bl r1_health_sync_provider_00063ad8\nldr r0,[sp,#8]\npop {r1,r2,r3,r4,r5,pc}\n"
 "1: adr r0,4f\nbl r1_native_printf\nmov r0,r4\nbl r1_fdb_native_db_path\nmov r2,r0\n"
 "adr r0,5f\nldr r1,[r4]\nbl r1_native_printf\nadr r0,6f\nldr r1,[r4]\nbl r1_native_printf\n"
 "movs r0,#0\npop {r1,r2,r3,r4,r5,pc}\n"
 "3: .word r1_fdb_native_query_count_cb\n"
 "4: .asciz \"[FlashDB][tsl]\"\n.space 1,0\n"
 "5: .asciz \"[%s][%s] \"\n.space 2,0\n"
 "6: .asciz \"Error: TSL (%s) isn't initialize OK.\\n\"\n.space 1,0\n");
}
__attribute__((naked,section(".text.r1_fdb_native_query_count_cb")))
void r1_fdb_native_query_count_cb(void) {
 __asm__ volatile("ldrb r0,[r0]\nldrb r2,[r1]\ncmp r0,r2\nbne 1f\nldr r0,[r1,#4]\nadds r0,r0,#1\nstr r0,[r1,#4]\n1: movs r0,#0\nbx lr\n");
}
/* Native FILE_MODE-off path behavior, including low-byte flag semantics. */
__attribute__((naked,section(".text.r1_fdb_native_db_path")))
void r1_fdb_native_db_path(void) {
 __asm__ volatile("ldrb r1,[r0,#25]\ncbz r1,1f\nmovs r0,#0\nbx lr\n1: ldr r0,[r0,#8]\nadds r0,r0,#4\nbx lr\n");
}
