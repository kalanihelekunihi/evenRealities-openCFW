#include <stdint.h>
#include <stddef.h>
typedef void (*r1_qma_event)(void);
struct r1_qma_runtime {uint8_t address;uint8_t padding[3];r1_qma_event double_tap,any_motion;};
_Static_assert(sizeof(struct r1_qma_runtime)==12 && offsetof(struct r1_qma_runtime,double_tap)==4 && offsetof(struct r1_qma_runtime,any_motion)==8,"native QMA runtime prefix");
/* Exact cold runtime record; distinct from the sensor-state address at2001e4b0. */
struct r1_qma_runtime r1_qma_runtime __attribute__((section(".r1.qma.runtime"),aligned(4)))={.address=0x12};
__attribute__((naked)) uint32_t r1_qma_delay_units(void)
{
 __asm__ volatile("push {r4,r5,r6,r7,r8,lr}\nmovs r4,r0\nbeq 2f\nldr r6,=r1_rtt_delay_cycles\nmov.w r7,#64000\n1: mov r5,r6\nmov r0,r7\nblx r5\nsubs r4,r4,#1\nbne 1b\n2: pop {r4,r5,r6,r7,r8,pc}\n");
}
__attribute__((naked)) uint32_t r1_qma_read_retry(void)
{
 __asm__ volatile("push {r4,r5,r6,r7,r8,r9,r10,lr}\nmovs r5,#0\nmov r7,r2\nmov r8,r1\nmov r9,r0\nmov r4,r5\nldr r6,=r1_qma_runtime\nb 2f\n1: mov r3,r7\nmov r2,r8\nmov r1,r9\nldrb r0,[r6]\nbl r1_motion_bus_read_request\ncbz r0,3f\nmovs r0,#1\n4: pop {r4,r5,r6,r7,r8,r9,r10,pc}\n3: movs r0,#5\nbl r1_qma_delay_units\n2: mov r0,r4\nadds r4,r4,#1\ncmp r0,#5\nblt 1b\nmov r0,r5\nb 4b\n");
}
__attribute__((naked)) uint32_t r1_qma_write_retry(void)
{
 __asm__ volatile("push {r0,r1,r4,r5,r6,r7,r8,lr}\nmovs r5,#0\nmov r7,r0\nmov r4,r5\nldr r6,=r1_qma_runtime\nb 2f\n1: movs r3,#1\nadd r2,sp,#4\nmov r1,r7\nldrb r0,[r6]\nbl r1_motion_bus_write_request\ncbz r0,2f\nmovs r0,#1\n3: pop {r2,r3,r4,r5,r6,r7,r8,pc}\n2: mov r0,r4\nadds r4,r4,#1\ncmp r0,#5\nblt 1b\nmov r0,r5\nb 3b\n");
}
__attribute__((naked)) uint32_t r1_qma6100_chip_id(void)
{ __asm__ volatile("push {r3,lr}\nmovs r2,#1\nmov r1,sp\nmovs r0,#0\nbl r1_qma_read_retry\nldrb r0,[sp]\npop {r3,pc}\n"); }
__attribute__((naked)) uint32_t r1_qma6100_irq_boundary(void)
{
 __asm__ volatile("push {r3,r4,r5,lr}\nmovs r0,#0\nmov r4,r0\nstr r0,[sp]\nb 2f\n1: movs r2,#4\nmov r1,sp\nmovs r0,#9\nbl r1_qma_read_retry\nuxtb r0,r0\ncmp r0,#1\nbeq 3f\ncbz r0,2f\n3: ldrb r0,[sp]\nldr r4,=r1_qma_runtime\nlsls r0,r0,#29\nbeq 4f\nldr r0,[r4,#8]\ncbz r0,4f\nblx r0\n4: ldrb r0,[sp,#1]\nlsls r0,r0,#26\nbpl 5f\nldr r0,[r4,#4]\ncmp r0,#0\nbeq 5f\nblx r0\n5: pop {r3,r4,r5,pc}\n2: mov r0,r4\nadds r4,r4,#1\ncmp r0,#10\nblt 1b\npop {r3,r4,r5,pc}\n");
}

const char r1_qma_fifo_string_870bc[36] __attribute__((section(".r1.qma.fifo.s870bc")))="[RING]qma6100_read_fifo state error";
const char r1_qma_fifo_string_870e0[32] __attribute__((section(".r1.qma.fifo.s870e0")))="qma6100_read_fifo state error";
const char r1_qma_fifo_string_87100[40] __attribute__((section(".r1.qma.fifo.s87100")))="[RING]qma6100_read_fifo depth(%d) error";
const char r1_qma_fifo_string_87128[36] __attribute__((section(".r1.qma.fifo.s87128")))="qma6100_read_fifo depth(%d) error";
__attribute__((naked)) uint32_t r1_qma6100_bounded_fifo_read(void) { __asm__ volatile("Q_86ff4:\npush {r3,r4,r5,r6,r7,lr}\nQ_86ff6:\nmov r6, r1\nQ_86ff8:\nmovs r7, r0\nQ_86ffa:\nmov.w r4, #0xffffffff\nQ_86ffe:\nbeq Q_87048\nQ_87000:\nmovs r2, #0x1\nQ_87002:\nmov r1, sp\nQ_87004:\nmovs r0, #0xe\nQ_87006:\nbl r1_qma_read_retry\nQ_8700a:\nldr r1,=0xc44fc\nQ_8700c:\nldr r3,=0xc441c\nQ_8700e:\nmovs r2, #0x1\nQ_87010:\nsubs r1, r1, r3\nQ_87012:\nlsrs r1, r1, #0x3\nQ_87014:\nadd.w r5, r2, r1, lsl #0x10\nQ_87018:\ncmp r0, #0x1\nQ_8701a:\nbeq Q_8704c\nQ_8701c:\nbl r1_structured_log_mode_get\nQ_87020:\nlsls r0, r0, #0x1f\nQ_87022:\nbne Q_8702c\nQ_87024:\nbl r1_structured_log_mode_get\nQ_87028:\nlsls r0, r0, #0x1d\nQ_8702a:\nbpl Q_87038\nQ_8702c:\nldr r2,=r1_qma_fifo_string_870bc\nQ_8702e:\nldr r1,=r1_qma_fifo_string_870bc\nQ_87030:\nmov.w r0, #0x4000000\nQ_87034:\nbl r1_structured_log_format\nQ_87038:\nbl r1_structured_log_mode_get\nQ_8703c:\nlsls r0, r0, #0x1e\nQ_8703e:\nbpl Q_87048\nQ_87040:\nmov r0, r5\nQ_87042:\nldr r1,=r1_qma_fifo_string_870e0\nQ_87044:\nbl nrf_log_frontend_std_0\nQ_87048:\nmov r0, r4\nQ_8704a:\npop {r3,r4,r5,r6,r7,pc}\nQ_8704c:\nldrb.w r0, [sp,#0x0]\nQ_87050:\nand r4, r0, #0x7f\nQ_87054:\ncmp r4, #0x40\nQ_87056:\nbls Q_8708c\nQ_87058:\nbl r1_structured_log_mode_get\nQ_8705c:\nlsls r0, r0, #0x1f\nQ_8705e:\nbne Q_87068\nQ_87060:\nbl r1_structured_log_mode_get\nQ_87064:\nlsls r0, r0, #0x1d\nQ_87066:\nbpl Q_87076\nQ_87068:\nmov r3, r4\nQ_8706a:\nldr r2,=r1_qma_fifo_string_87100\nQ_8706c:\nldr r1,=r1_qma_fifo_string_87100\nQ_8706e:\nmov.w r0, #0x4400000\nQ_87072:\nbl r1_structured_log_format\nQ_87076:\nbl r1_structured_log_mode_get\nQ_8707a:\nlsls r0, r0, #0x1e\nQ_8707c:\nbpl Q_87088\nQ_8707e:\nmov r0, r5\nQ_87080:\nmov r2, r4\nQ_87082:\nldr r1,=r1_qma_fifo_string_87128\nQ_87084:\nbl nrf_log_frontend_std_1\nQ_87088:\nmovs r0, #0x0\nQ_8708a:\npop {r3,r4,r5,r6,r7,pc}\nQ_8708c:\ncmp r6, r4\nQ_8708e:\nbls Q_87092\nQ_87090:\nmov r6, r4\nQ_87092:\nadd.w r0, r6, r6, lsl #0x1\nQ_87096:\nmovw r1, #0xffff\nQ_8709a:\nand.w r2, r1, r0, lsl #0x1\nQ_8709e:\nmov r1, r7\nQ_870a0:\nmovs r0, #0x3f\nQ_870a2:\nbl r1_qma_read_retry\nQ_870a6:\nmovs r1, #0x87\nQ_870a8:\nmovs r0, #0x3e\nQ_870aa:\nbl r1_qma_write_retry\nQ_870ae:\nmov r0, r6\nQ_870b0:\npop {r3,r4,r5,r6,r7,pc}\n"); }
