#include <stdint.h>
__attribute__((naked)) uint32_t r1_bma4_get_fifo_length(void)
{
 __asm__ volatile("push {r3,r4,r5,lr}\nmov r4,r0\nmovs r0,#0\nstr r0,[sp]\nmov r5,r1\nmov r0,r1\nbl r1_bma4_null_pointer_check\ncbnz r0,1f\ncbz r4,1f\nmov r3,r5\nmovs r2,#2\nmov r1,sp\nmovs r0,#36\nbl r1_bma4_read_regs_boundary\ncmp r0,#0\nbne 2f\nldrb r0,[sp,#1]\nbl r1_bma_fifo_length_msb\nstrb r0,[sp,#1]\nldrh r1,[sp]\nstrh r1,[r4]\nmovs r0,#0\n2: pop {r3,r4,r5,pc}\n1: mov.w r0,#0xffffffff\npop {r3,r4,r5,pc}\n");
}
__attribute__((naked)) uint32_t r1_bma_fifo_read_bytes(void)
{
 __asm__ volatile("push {r3,r4,r5,r6,r7,r8,r9,lr}\nmov r8,r0\nmovs r0,#0\nstrh r0,[sp]\nmov r5,r1\nmov r4,r2\nmovs r6,#38\nmov r0,r2\nbl r1_bma4_null_pointer_check\ncbnz r0,3f\ncmp r8,#0\nbeq 3f\ncbz r5,3f\nldrb r0,[r4,#8]\ncbnz r0,1f\nmovs r6,#166\n1: mov r1,r4\nmov r0,sp\nbl r1_bma4_get_fifo_length\nmvn r7,#1\ncbnz r0,2f\nldrh r0,[sp]\ncmp r0,#0\nbeq 4f\ncmp r0,r5\nbls 5f\nstrh r5,[sp]\n5: ldr r5,[r4,#36]\nldrh r2,[sp]\nmov r1,r8\nmov r0,r6\nldr r3,[r4,#4]\nblx r5\nstrb r0,[r4,#9]\ncbz r0,6f\n2: mov r0,r7\n4: pop {r3,r4,r5,r6,r7,r8,r9,pc}\n3: mov.w r0,#0xffffffff\nb 4b\n6: ldrh r0,[sp]\nsxth r0,r0\nb 4b\n");
}
#define LOG_FAIL(ring,sdk,value,exit_label) "bl r1_structured_log_mode_get\nlsls r0,r0,#31\nbne 1f\nbl r1_structured_log_mode_get\nlsls r0,r0,#29\nbpl 2f\n1: mov r3," #value "\nldr r2,=" #ring "\nldr r1,=" #ring "\nmov r0,r9\nbl r1_structured_log_format\n2: bl r1_structured_log_mode_get\nlsls r0,r0,#30\nbpl " #exit_label "\nmov r0,r4\nmov r2," #value "\nldr r1,=" #sdk "\nbl nrf_log_frontend_std_1\nb " #exit_label "\n"
__attribute__((naked)) uint32_t r1_bma456w_fifo_read(void)
{
 __asm__ volatile("push {r4,r5,r6,r7,r8,r9,r10,lr}\nmov r7,r1\nmovs r8,r0\nmov.w r6,#0xffffffff\nbeq 9f\ncmp r7,#0\nbeq 9f\nldr r1,=r1_bma_context\nmovs r0,#0\nbl r1_bma4_set_advance_power_save_boundary\nmovs r5,r0\nmov.w r9,#0x4400000\nldr r4,=0x1c0001\nbeq 3f\n"
 LOG_FAIL(r1_bma_fifo_disable_ring,r1_bma_fifo_disable_sdk,r5,8f)
 "3: movs r1,#0\nmov.w r0,#450\nbl r1_bma_delay_us\nadd r0,r7,r7,lsl #1\nmovw r1,#65535\nand r1,r1,r0,lsl #1\nldr r2,=r1_bma_context\nmov r0,r8\nbl r1_bma_fifo_read_bytes\nmovs r5,r0\nbpl 4f\n"
 LOG_FAIL(r1_bma_fifo_read_ring,r1_bma_fifo_read_sdk,r5,9f)
 "4: ldr r1,=r1_bma_context\nmovs r0,#1\nbl r1_bma4_set_advance_power_save_boundary\nmovs r6,r0\nbeq 5f\n"
 LOG_FAIL(r1_bma_fifo_enable_ring,r1_bma_fifo_enable_sdk,r6,8f)
 "8: movs r0,#0\nb 10f\n9: mov r0,r6\n10: pop {r4,r5,r6,r7,r8,r9,r10,pc}\n5: movs r0,#6\nsdiv r0,r5,r0\nb 10b\n");
}
const char r1_bma_fifo_disable_ring[52] __attribute__((section(".r1.bma.fifo.disable_ring")))="[RING]BMA456 disable advance power save failed: %d";
const char r1_bma_fifo_disable_sdk[48] __attribute__((section(".r1.bma.fifo.disable_sdk")))="BMA456 disable advance power save failed: %d";
const char r1_bma_fifo_read_ring[40] __attribute__((section(".r1.bma.fifo.read_ring")))="[RING]BMA456 read fifo data failed: %d";
const char r1_bma_fifo_read_sdk[36] __attribute__((section(".r1.bma.fifo.read_sdk")))="BMA456 read fifo data failed: %d";
const char r1_bma_fifo_enable_ring[52] __attribute__((section(".r1.bma.fifo.enable_ring")))="[RING]BMA456 enable advance power save failed: %d";
const char r1_bma_fifo_enable_sdk[44] __attribute__((section(".r1.bma.fifo.enable_sdk")))="BMA456 enable advance power save failed: %d";
