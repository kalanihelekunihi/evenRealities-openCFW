#include <stdint.h>
/* Native outer/provider frames keep stack-backed register requests attributable. */
__attribute__((naked)) uint32_t lis2dw12_pin_int1_route_get(void)
{ __asm__ volatile("push {r4,lr}\nmov r2,r1\nmovs r3,#1\nmovs r1,#35\nbl lis2dw12_read_reg\npop {r4,pc}\n"); }
__attribute__((naked)) uint32_t lis2dw12_pin_int1_route_set(void)
{
 __asm__ volatile("push {r2,r3,r4,r5,r6,lr}\nmov r4,r1\nmov r5,r0\nmovs r3,#1\nadd r2,sp,#4\nmovs r1,#36\nbl lis2dw12_read_reg\ncmp r0,#0\nbne 1f\nmovs r3,#1\nmov r2,sp\nmovs r1,#63\nmov r0,r5\nbl lis2dw12_read_reg\ncmp r0,#0\nbne 1f\nldrb r0,[r4]\nldrb r1,[sp,#4]\nldrb r2,[sp]\nbl r1_lis_int1_route_byte\nstrb r0,[sp]\nmovs r3,#1\nmov r2,r4\nmovs r1,#35\nmov r0,r5\nbl lis2dw12_write_reg\ncmp r0,#0\nbne 1f\nmovs r3,#1\nmov r2,sp\nmovs r1,#63\nmov r0,r5\nbl lis2dw12_write_reg\n1: pop {r2,r3,r4,r5,r6,pc}\n");
}
#define SETTER(name,value) "movs r1,#" #value "\nldr r0,=r1_lis_context\nbl " #name "\n"
#define LOG_TAP(ring,sdk) "bl r1_structured_log_mode_get\nlsls r0,r0,#31\nbne 1f\nbl r1_structured_log_mode_get\nlsls r0,r0,#29\nbpl 2f\n1: ldr r2,=" #ring "\nldr r1,=" #ring "\nmov.w r0,#0xc000000\nbl r1_structured_log_format\n2: bl r1_structured_log_mode_get\nlsls r0,r0,#30\nbpl 3f\nldr r0,=0x1c0003\nldr r1,=" #sdk "\nbl nrf_log_frontend_std_0\n3: movs r0,#1\npop {r3,pc}\n"
__attribute__((naked)) uint32_t r1_lis2dw12_aux20_boundary(void)
{
 __asm__ volatile("push {r3,lr}\nmov r1,sp\nldr r0,=r1_lis_context\nbl lis2dw12_pin_int1_route_get\nldrb r0,[sp]\nmov r1,sp\nbic r0,r0,#8\nstrb r0,[sp]\nldr r0,=r1_lis_context\nbl lis2dw12_pin_int1_route_set\n"
 SETTER(lis2dw12_tap_detection_on_z_set,0) SETTER(lis2dw12_tap_detection_on_y_set,0) SETTER(lis2dw12_tap_detection_on_x_set,0) SETTER(lis2dw12_tap_mode_set,0) SETTER(lis2dw12_full_scale_set,2) SETTER(lis2dw12_data_rate_set,3)
 LOG_TAP(r1_lis_tap_disable_ring,r1_lis_tap_disable_sdk));
}
__attribute__((naked)) uint32_t r1_lis2dw12_aux16_boundary(void)
{
 __asm__ volatile("push {r3,lr}\n"
 SETTER(lis2dw12_tap_detection_on_z_set,1) SETTER(lis2dw12_tap_detection_on_y_set,1) SETTER(lis2dw12_tap_detection_on_x_set,1) SETTER(lis2dw12_tap_threshold_x_set,3) SETTER(lis2dw12_tap_threshold_y_set,3) SETTER(lis2dw12_tap_threshold_z_set,3) SETTER(lis2dw12_tap_dur_set,0) SETTER(lis2dw12_tap_quiet_set,0) SETTER(lis2dw12_tap_shock_set,0) SETTER(lis2dw12_tap_mode_set,1)
 "mov r1,sp\nldr r0,=r1_lis_context\nbl lis2dw12_pin_int1_route_get\nldrb r0,[sp]\nmov r1,sp\norr r0,r0,#8\nstrb r0,[sp]\nldr r0,=r1_lis_context\nbl lis2dw12_pin_int1_route_set\n"
 LOG_TAP(r1_lis_tap_enable_ring,r1_lis_tap_enable_sdk));
}
const char r1_lis_tap_disable_ring[36] __attribute__((section(".r1.lis.tap.disable_ring")))="[RING]LIS2DOC double tap disabled";
const char r1_lis_tap_disable_sdk[28] __attribute__((section(".r1.lis.tap.disable_sdk")))="LIS2DOC double tap disabled";
const char r1_lis_tap_enable_ring[52] __attribute__((section(".r1.lis.tap.enable_ring")))="[RING]LIS2DOC double tap enabled (ODR=400Hz, FS=2g)";
const char r1_lis_tap_enable_sdk[48] __attribute__((section(".r1.lis.tap.enable_sdk")))="LIS2DOC double tap enabled (ODR=400Hz, FS=2g)";
