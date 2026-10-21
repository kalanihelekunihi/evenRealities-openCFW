#include <stdint.h>
/* Raw register/stack interfaces follow the observed ARM entry contracts. */
__attribute__((naked)) uint32_t r1_bma4_set_accel_enable(void)
{
 __asm__ volatile("push {r3,r4,r5,r6,r7,lr}\nmov r6,r0\nmovs r0,#0\nstrb r0,[sp]\nmov r5,r1\nmov r0,r1\nbl r1_bma4_null_pointer_check\nmovs r4,r0\nbne 1f\nmov r3,r5\nmovs r2,#1\nmov r1,sp\nmovs r0,#125\nbl r1_bma4_read_regs_boundary\nmovs r4,r0\nbne 1f\nldrb r0,[sp]\nmov r1,r6\nbl r1_bma_accel_enable_byte\nstrb r0,[sp]\nmov r3,r5\nmovs r2,#1\nmov r1,sp\nmovs r0,#125\nbl r1_bma4_write_regs_boundary\nmov r4,r0\nldr r2,[r5,#44]\nmovw r0,#25000\nldr r1,[r5,#4]\nblx r2\n1: mov r0,r4\npop {r3,r4,r5,r6,r7,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma4_set_accel_config(void)
{
 __asm__ volatile("push {r3,r4,r5,lr}\nmov r4,r0\nmovs r0,#0\nstr r0,[sp]\nmov r5,r1\nmov r0,r1\nbl r1_bma4_null_pointer_check\ncbnz r0,1f\ncbz r4,1f\nldrb r2,[r4,#2]\nldrb r1,[r4,#1]\nldrb r0,[r4]\nbl r1_bma_validate_accel_parameters\ncmp r0,#0\nbne 2f\nldrb r0,[r4]\nmov r3,r5\nand r0,r0,#15\nstrb r0,[sp]\nldrb r1,[r4,#1]\nmovs r2,#1\norr r0,r0,r1,lsl #4\nldrb r1,[r4,#2]\norr r0,r0,r1,lsl #7\nstrb r0,[sp]\nldrb r0,[r4,#3]\nadd r1,sp,#1\nand r0,r0,#3\nstrb r0,[sp,#1]\nmovs r0,#65\nbl r1_bma4_write_regs_boundary\ncmp r0,#0\nbne 2f\nmov r3,r5\nmovs r2,#1\nmov r1,sp\nmovs r0,#64\nbl r1_bma4_write_regs_boundary\nldrb r1,[sp]\nlsrs r1,r1,#7\nstrb r1,[r5,#50]\n2: pop {r3,r4,r5,pc}\n1: mov.w r0,#0xffffffff\npop {r3,r4,r5,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma4_set_fifo_config(void)
{
 __asm__ volatile("push {r3,r4,r5,r6,r7,lr}\nmov r7,r0\nmovs r0,#0\nstr r0,[sp]\nmov r6,r1\nmov r4,r2\nmov r0,r2\nbl r1_bma4_null_pointer_check\ncmp r0,#0\nbne 1f\nmov r3,r4\nmovs r2,#2\nmov r1,sp\nmovs r0,#72\nbl r1_bma4_read_regs_boundary\ncmp r0,#0\nbne 1f\nldrh r0,[sp]\nmov r1,r7\nmov r2,r6\nbl r1_bma_fifo_config_bytes\nstrb r0,[sp]\nlsrs r0,r0,#8\nstrb r0,[sp,#1]\nmov r3,r4\nmovs r2,#1\nmov r1,sp\nmovs r0,#72\nbl r1_bma4_write_regs_boundary\ncmp r0,#0\nbne 1f\nldr r2,[r4,#44]\nmov.w r0,#1000\nldr r1,[r4,#4]\nblx r2\nmov r3,r4\nmovs r2,#1\nmovs r0,#73\nadd r1,sp,#1\nbl r1_bma4_write_regs_boundary\n1: pop {r3,r4,r5,r6,r7,pc}\n");
}
