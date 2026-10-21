#include <stdint.h>
__attribute__((naked)) uint32_t r1_bma4_write_regs_direct(void)
{
 __asm__ volatile("push {r4,r5,r6,r7,r8,lr}\nmov r6,r0\nmov r8,r2\nmov r7,r1\nmov r4,r3\nmov r0,r3\nbl r1_bma4_null_pointer_check\nmovs r5,r0\nbne 4f\ncbz r7,4f\nldrb r0,[r4,#8]\ncbnz r0,1f\nand r6,r6,#127\n1: ldr r12,[r4,#40]\nmov r2,r8\nmov r1,r7\nmov r0,r6\nldr r3,[r4,#4]\nblx r12\nstrb r0,[r4,#9]\ncbz r0,2f\nmvn r5,#1\nb 5f\n2: ldrb r0,[r4,#50]\nldr r2,[r4,#44]\nldr r1,[r4,#4]\ncmp r0,#1\nbeq 3f\nmov.w r0,#450\nblx r2\nb 5f\n3: movs r0,#2\nblx r2\nb 5f\n4: mov.w r5,#0xffffffff\n5: mov r0,r5\npop {r4,r5,r6,r7,r8,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma4_set_advance_power_save_boundary(void)
{
 __asm__ volatile("push {r3,r4,r5,lr}\nmov r4,r0\nmovs r0,#0\nstrb r0,[sp]\nmov r5,r1\nmov r0,r1\nbl r1_bma4_null_pointer_check\ncmp r0,#0\nbne 1f\nmov r3,r5\nmovs r2,#1\nmov r1,sp\nmovs r0,#124\nbl r1_bma4_read_regs_boundary\ncmp r0,#0\nbne 1f\nldrb r0,[sp]\nmov r1,r4\nbl r1_bma_power_update_byte\nstrb r0,[sp]\nmov r3,r5\nmovs r2,#1\nmov r1,sp\nmovs r0,#124\nbl r1_bma4_write_regs_boundary\n1: pop {r3,r4,r5,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma4_write_regs_boundary(void)
{
 __asm__ volatile("push {r3,r4,r5,r6,r7,lr}\nmov r7,r0\nmovs r0,#0\nstrb r0,[sp]\nmov r5,r2\nmov r6,r1\nmov r4,r3\nmov r0,r3\nbl r1_bma4_null_pointer_check\ncbnz r0,5f\ncbz r6,5f\ncmp r7,#94\nbeq 1f\nmov r3,r4\nmov r2,r5\nmov r1,r6\nmov r0,r7\nbl r1_bma4_write_regs_direct\npop {r3,r4,r5,r6,r7,pc}\n1: mov r1,r4\nmov r0,sp\nbl r1_bma4_get_advance_power_save\nmov r1,r0\nldrb r0,[sp]\ncmp r0,#1\nbne 2f\ncbnz r1,2f\nmov r1,r4\nmovs r0,#0\nbl r1_bma4_set_advance_power_save_boundary\nmov r1,r0\n2: lsls r2,r5,#31\nmvn r0,#9\nbne 6f\nldrb r2,[r4,#22]\ncmp r2,r5\nbcc 6f\ncmp r1,#0\nbne 6f\nldrh r0,[r4,#20]\ncmp r0,r5\nbcs 3f\nmov r2,r4\nmov r1,r5\nmov r0,r6\nbl r1_bma4_feature_chunk_write\nb 4f\n3: mov r3,r4\nmov r2,r5\nmov r1,r6\nmovs r0,#94\nbl r1_bma4_write_regs_direct\n4: cmp r0,#0\nbne 6f\nldrb r1,[sp]\ncmp r1,#1\nbne 6f\nmov r1,r4\nmovs r0,#1\nbl r1_bma4_set_advance_power_save_boundary\npop {r3,r4,r5,r6,r7,pc}\n5: mov.w r0,#0xffffffff\n6: pop {r3,r4,r5,r6,r7,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma4_feature_address_reset(void)
{
 __asm__ volatile("push {r4,lr}\nmov r4,r0\nbl r1_bma4_null_pointer_check\ncmp r0,#0\nbne 1f\nmov r3,r4\nmovs r2,#1\nadd r1,r4,#23\nmovs r0,#91\nbl r1_bma4_write_regs_direct\ncmp r0,#0\nbne 1f\nmov r3,r4\nadd r1,r4,#24\nmovs r2,#1\npop {r4,lr}\nmovs r0,#92\nb r1_bma4_write_regs_direct\n1: pop {r4,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma4_feature_address_increment(void)
{
 __asm__ volatile("push {r2,r3,r4,r5,r6,lr}\nmov r4,r0\nmovs r0,#0\nstrb r0,[sp]\nstrb r0,[sp,#4]\nmov r0,r4\nbl r1_bma4_null_pointer_check\ncmp r0,#0\nbne 2f\nmov r3,r4\nmovs r2,#1\nmov r1,sp\nmovs r0,#91\nbl r1_bma4_read_regs_direct\nmvn r5,#1\ncbnz r0,1f\nmov r3,r4\nmovs r2,#1\nadd r1,sp,#4\nmovs r0,#92\nbl r1_bma4_read_regs_direct\ncbz r0,3f\n1: mov r0,r5\n2: pop {r2,r3,r4,r5,r6,pc}\n3: ldrb r1,[sp,#4]\nldrb r0,[sp]\nmov r2,r4\nbl r1_bma_feature_address_bytes\nstrb r0,[sp]\nlsrs r0,r0,#8\nstrb r0,[sp,#4]\nmov r3,r4\nmovs r2,#1\nmov r1,sp\nmovs r0,#91\nbl r1_bma4_write_regs_direct\ncmp r0,#0\nbne 2b\nmov r3,r4\nmovs r2,#1\nadd r1,sp,#4\nmovs r0,#92\nbl r1_bma4_write_regs_direct\npop {r2,r3,r4,r5,r6,pc}\n");
}
/* Native full chunk loop continues after errors; index advances only when the
 * transfer and feature-address increment both succeed. No early break added. */
#define CHUNKS(name,transfer) __attribute__((naked)) uint32_t name(void) { __asm__ volatile("push {r4,r5,r6,r7,r8,r9,r10,lr}\nmov r9,r0\nldrh r0,[r2,#20]\nmov r4,r2\nudiv r7,r1,r0\nudiv r2,r1,r0\nmls r0,r0,r2,r1\nuxth r8,r0\nmovs r5,#0\nmov r0,r4\nbl r1_bma4_feature_address_reset\ncmp r0,#0\nbne 4f\nmovs r6,#0\nb 2f\n1: ldrh r2,[r4,#20]\nadd r1,r9,r5\nmov r3,r4\nmovs r0,#94\nbl " #transfer "\ncbnz r0,5f\nmov r0,r4\nbl r1_bma4_feature_address_increment\ncbnz r0,5f\nldrh r1,[r4,#20]\nadd r1,r5\nuxth r5,r1\n5: adds r6,r6,#1\n2: cmp r6,r7\nbcc 1b\ncmp r8,#0\nbeq 3f\ncmp r0,#0\nbne 4f\nadd r1,r9,r5\nmov r3,r4\nmov r2,r8\nmovs r0,#94\nbl " #transfer "\n3: cmp r0,#0\nbne 4f\nmov r0,r4\npop {r4,r5,r6,r7,r8,r9,r10,lr}\nb r1_bma4_feature_address_reset\n4: pop {r4,r5,r6,r7,r8,r9,r10,pc}\n"); }
CHUNKS(r1_bma4_feature_chunk_read_boundary,r1_bma4_read_regs_direct)
CHUNKS(r1_bma4_feature_chunk_write,r1_bma4_write_regs_direct)
