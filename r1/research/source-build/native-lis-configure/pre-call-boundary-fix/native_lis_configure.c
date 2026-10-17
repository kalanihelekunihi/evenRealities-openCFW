#include <stdint.h>
/* Authenticated native strings, including their observed padding. */
const char r1_lis_id_ring[28] __attribute__((section(".r1.lis.config.id_ring")))="[RING]LIS2DOC_ID not found";
const char r1_lis_id_sdk[24] __attribute__((section(".r1.lis.config.id_sdk")))="LIS2DOC_ID not found";
const char r1_lis_reset_ring[28] __attribute__((section(".r1.lis.config.reset_ring")))="[RING]LIS2DOC_RESET failed";
const char r1_lis_reset_sdk[24] __attribute__((section(".r1.lis.config.reset_sdk")))="LIS2DOC_RESET failed";
/* Native64-byte outer frame:40 local bytes plus six saved registers. Calls
 * return to that frame before subsequent providers run. Retry/error order and
 * caller-scratch inputs are preserved; no hardened status policy is invented. */
__attribute__((naked)) uint32_t r1_lis2dw12_configure_boundary(void)
{
 __asm__ volatile(
 "push {r4,r5,r6,r7,r8,lr}\nmov r5,r0\nldr r0,=r1_lis_context\nsub sp,#40\nldr r1,=r1_lis_default_write\nstr r1,[r0]\nldr r1,=r1_lis_default_read\nstr r1,[r0,#4]\nmovs r6,#0\nstrb r6,[sp,#32]\nadd r1,sp,#32\nbl r1_lis_device_id_get\nldrb r1,[sp,#32]\nldr r4,=0x1c0001\nmov.w r8,#0x4000000\ncmp r1,#0x44\nbeq 2f\n"
 "bl r1_structured_log_mode_get\nlsls r0,r0,#31\nbne 1f\nbl r1_structured_log_mode_get\nlsls r0,r0,#29\nbpl 11f\n1: ldr r2,=r1_lis_id_ring\nldr r1,=r1_lis_id_ring\nmov r0,r8\nbl r1_structured_log_format\n11: bl r1_structured_log_mode_get\nlsls r0,r0,#30\nbpl 9f\nmov r0,r4\nldr r1,=r1_lis_id_sdk\nb 8f\n"
 "2: movs r1,#1\nldr r0,=r1_lis_context\nbl lis2dw12_reset_set\nmovs r7,#0\nstrb r6,[sp,#36]\n3: add r1,sp,#36\nldr r0,=r1_lis_context\nbl lis2dw12_reset_get\nmovs r0,#2\nbl nrf_delay_ms\nmov r0,r7\nadds r7,r7,#1\nuxtb r7,r7\ncmp r0,#10\nbls 5f\n"
 "bl r1_structured_log_mode_get\nlsls r0,r0,#31\nbne 4f\nbl r1_structured_log_mode_get\nlsls r0,r0,#29\nbpl 12f\n4: ldr r2,=r1_lis_reset_ring\nldr r1,=r1_lis_reset_ring\nmov r0,r8\nbl r1_structured_log_format\n12: bl r1_structured_log_mode_get\nlsls r0,r0,#30\nbpl 9f\nmov r0,r4\nldr r1,=r1_lis_reset_sdk\n8: bl nrf_log_frontend_std_0\n9: movs r0,#0\n10: add sp,#40\npop {r4,r5,r6,r7,r8,pc}\n"
 "5: ldrb r0,[sp,#36]\ncmp r0,#0\nbne 3b\nldr r0,=r1_lis_context\nbl r1_lis_reg17_bit6_enable\nmovs r1,#1\nldr r0,=r1_lis_context\nbl lis2dw12_block_data_update_set\nmovs r1,#2\nldr r0,=r1_lis_context\nbl lis2dw12_full_scale_set\nmovs r1,#0\nldr r0,=r1_lis_context\nbl lis2dw12_filter_path_set\nmovs r1,#1\nldr r0,=r1_lis_context\nbl lis2dw12_filter_bandwidth_set\nmovs r1,#31\nldr r0,=r1_lis_context\nbl lis2dw12_fifo_watermark_set\nmovs r1,#6\nldr r0,=r1_lis_context\nbl lis2dw12_fifo_mode_set\norr r1,r6,#10\nldr r0,=r1_lis_context\nbl r1_lis_native_power_mode_set\n"
 "cmp r5,#100\nbeq 6f\nbgt 7f\ncmp r5,#25\nbeq 13f\ncmp r5,#50\nbne 13f\nmovs r1,#4\nb 14f\n7: cmp r5,#150\nbeq 15f\ncmp r5,#200\nbeq 15f\n13: movs r1,#3\nb 14f\n6: movs r1,#5\nb 14f\n15: movs r1,#6\n14: ldr r0,=r1_lis_context\nbl lis2dw12_data_rate_set\nmovs r0,#100\nbl nrf_delay_ms\nmovs r1,#5\nmov r0,sp\nbl r1_lis2dw12_fifo_read\nmovs r0,#1\nb 10b\n");
}
