/* Register-only entry bridges; r0/r1 and incoming r3 are native ABI inputs. */
#include <stdint.h>
__attribute__((naked)) uint32_t lis2dw12_block_data_update_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_block_data_update_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_fifo_mode_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_fifo_mode_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_fifo_watermark_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_fifo_watermark_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_filter_bandwidth_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_filter_bandwidth_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_full_scale_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_full_scale_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_reset_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_reset_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_detection_on_z_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_detection_on_z_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_detection_on_y_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_detection_on_y_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_detection_on_x_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_detection_on_x_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_dur_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_dur_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_mode_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_mode_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_quiet_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_quiet_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_shock_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_shock_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_threshold_x_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_threshold_x_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_threshold_y_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_threshold_y_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_tap_threshold_z_set(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_tap_threshold_z_set_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_reset_get(void) { __asm__ volatile("push {r3,r4,r5,lr}\nmov r2,sp\nbl lis2dw12_reset_get_body\npop {r3,r4,r5,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_write_reg(void) { __asm__ volatile("push {r4,r5}\nldr r4,[r0,#12]\nldr r5,[r0]\nmov r0,r4\nmov r12,r5\npop {r4,r5}\nbx r12\n"); }
