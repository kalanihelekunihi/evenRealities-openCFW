#include <stdint.h>
/* Native152-byte frame owns the128-byte callback buffer. Pure C copying runs
 * only after the callback returns, preserving the transport call boundary. */
__attribute__((naked)) uint32_t r1_bma4_read_regs_direct(void)
{
 __asm__ volatile("push {r4,r5,r6,r7,r8,lr}\nmov r7,r0\nsub sp,#128\nmov r6,r2\nmov r8,r1\nmov r4,r3\nmov r0,r3\nbl r1_bma4_null_pointer_check\nmovs r5,r0\nbne 3f\ncmp r8,#0\nbeq 3f\nldrb r0,[r4,#8]\ncbnz r0,1f\norr r7,r7,#128\n1: ldrb r0,[r4,#11]\nldr r12,[r4,#36]\nadds r2,r0,r6\nmov r1,sp\nmov r0,r7\nldr r3,[r4,#4]\nblx r12\nstrb r0,[r4,#9]\ncbz r0,2f\nmvn r5,#1\nb 4f\n2: mov r0,r8\nmov r1,sp\nmov r2,r6\nmov r3,r4\nbl r1_bma_copy_read_bytes\nb 4f\n3: mov.w r5,#0xffffffff\n4: add sp,#128\nmov r0,r5\npop {r4,r5,r6,r7,r8,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma4_read_regs_boundary(void)
{
 __asm__ volatile("push {r3,r4,r5,r6,r7,lr}\nmov r7,r0\nmovs r0,#0\nstrb r0,[sp]\nmov r5,r2\nmov r6,r1\nmov r4,r3\nmov r0,r3\nbl r1_bma4_null_pointer_check\ncbnz r0,5f\ncbz r6,5f\ncmp r7,#94\nbeq 1f\nmov r3,r4\nmov r2,r5\nmov r1,r6\nmov r0,r7\nbl r1_bma4_read_regs_direct\npop {r3,r4,r5,r6,r7,pc}\n1: mov r1,r4\nmov r0,sp\nbl r1_bma4_get_advance_power_save\nmov r1,r0\nldrb r0,[sp]\ncmp r0,#1\nbne 2f\nmov r1,r4\nmovs r0,#0\nbl r1_bma4_set_advance_power_save_boundary\nmov r1,r0\n2: lsls r2,r5,#31\nmvn r0,#9\nbne 6f\nldrb r2,[r4,#22]\ncmp r2,r5\nbcc 6f\ncmp r1,#0\nbne 6f\nldrh r0,[r4,#20]\ncmp r0,r5\nbcs 3f\nmov r2,r4\nmov r1,r5\nmov r0,r6\nbl r1_bma4_feature_chunk_read_boundary\nb 4f\n3: mov r3,r4\nmov r2,r5\nmov r1,r6\nmovs r0,#94\nbl r1_bma4_read_regs_direct\n4: cmp r0,#0\nbne 6f\nldrb r1,[sp]\ncmp r1,#1\nbne 6f\nmov r1,r4\nmovs r0,#1\nbl r1_bma4_set_advance_power_save_boundary\npop {r3,r4,r5,r6,r7,pc}\n5: mov.w r0,#0xffffffff\n6: pop {r3,r4,r5,r6,r7,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma4_get_advance_power_save(void)
{
 __asm__ volatile("push {r3,r4,r5,lr}\nmov r4,r0\nmovs r0,#0\nstrb r0,[sp]\nmov r5,r1\nmov r0,r1\nbl r1_bma4_null_pointer_check\ncbnz r0,1f\ncbz r4,1f\nmov r3,r5\nmovs r2,#1\nmov r1,sp\nmovs r0,#124\nbl r1_bma4_read_regs_boundary\ncmp r0,#0\nbne 2f\nldrb r1,[sp]\nand r1,r1,#1\nstrb r1,[r4]\n2: pop {r3,r4,r5,pc}\n1: mov.w r0,#0xffffffff\npop {r3,r4,r5,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma456w_identity_probe(void)
{
 __asm__ volatile("push {r3,r4,r5,r6,r7,lr}\nmovs r0,#0\nstrb r0,[sp]\nldr r0,=r1_bma_context\nmov.w r6,#0x4400000\nldr r2,[r0,#36]\nldr r4,=0x1c0001\ncmp r2,#0\nbne 3f\nldr r0,=r1_bma_context\nbl r1_bma_interface_initialize\nmovs r5,r0\nbeq 3f\nbl r1_structured_log_mode_get\nlsls r0,r0,#31\nbne 1f\nbl r1_structured_log_mode_get\nlsls r0,r0,#29\nbpl 2f\n1: mov r3,r5\nldr r2,=r1_bma_init_ring\nldr r1,=r1_bma_init_ring\nmov r0,r6\nbl r1_structured_log_format\n2: bl r1_structured_log_mode_get\nlsls r0,r0,#30\nbpl 6f\nmov r0,r4\nmov r2,r5\nldr r1,=r1_bma_init_sdk\nb 5f\n3: ldr r3,=r1_bma_context\nmovs r2,#1\nmov r1,sp\nmovs r0,#0\nbl r1_bma4_read_regs_boundary\nmovs r5,r0\nbeq 7f\nbl r1_structured_log_mode_get\nlsls r0,r0,#31\nbne 4f\nbl r1_structured_log_mode_get\nlsls r0,r0,#29\nbpl 8f\n4: mov r3,r5\nldr r2,=r1_bma_id_ring\nldr r1,=r1_bma_id_ring\nmov r0,r6\nbl r1_structured_log_format\n8: bl r1_structured_log_mode_get\nlsls r0,r0,#30\nbpl 6f\nmov r0,r4\nmov r2,r5\nldr r1,=r1_bma_id_sdk\n5: bl nrf_log_frontend_std_1\n6: movs r0,#0\npop {r3,r4,r5,r6,r7,pc}\n7: ldrb r0,[sp]\npop {r3,r4,r5,r6,r7,pc}\n");
}
const char r1_bma_init_ring[40] __attribute__((section(".r1.bma.id.init_ring")))="[RING]BMA456 interface init failed: %d";
const char r1_bma_init_sdk[36] __attribute__((section(".r1.bma.id.init_sdk")))="BMA456 interface init failed: %d";
const char r1_bma_id_ring[40] __attribute__((section(".r1.bma.id.id_ring")))="[RING]BMA456 read chip id failed: %d";
const char r1_bma_id_sdk[32] __attribute__((section(".r1.bma.id.id_sdk")))="BMA456 read chip id failed: %d";
