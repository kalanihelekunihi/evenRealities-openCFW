#include <stdint.h>
#include "native_lis_context.h"
#include "native_motion_operations.h"
/* Register requests use ordinary typed C interfaces. */
__attribute__((noinline)) int32_t lis2dw12_pin_int1_route_get(const stmdev_ctx_t *ctx,
                                  lis2dw12_ctrl4_int1_pad_ctrl_t *route)
{
 return lis2dw12_read_reg(ctx, 0x23, (uint8_t *)route, 1);
}
extern uint32_t r1_lis_int1_route_byte(uint32_t, uint32_t, uint32_t);
/* Preserve the two-read/two-write sequence; unwritten bytes start at zero. */
int32_t lis2dw12_pin_int1_route_set(const stmdev_ctx_t *ctx,
 lis2dw12_ctrl4_int1_pad_ctrl_t *route)
{
 volatile uint8_t frame[8]={0};
 int32_t status = lis2dw12_read_reg(ctx, 0x24,
                                  (uint8_t *)(uintptr_t)(frame+4), 1);
 if (status != 0)
  return status;
 status = lis2dw12_read_reg(ctx, 0x3f, (uint8_t *)(uintptr_t)frame, 1);
 if (status != 0)
  return status;
 uint32_t ctrl4 = *(const volatile uint8_t *)route;
 uint32_t ctrl5 = frame[4];
 uint32_t ctrl7 = frame[0];
 frame[0] = (uint8_t)r1_lis_int1_route_byte(ctrl4, ctrl5, ctrl7);
 status = lis2dw12_write_reg(ctx, 0x23, (uint8_t *)route, 1);
 if (status != 0)
  return status;
 return lis2dw12_write_reg(ctx, 0x3f,
                          (uint8_t *)(uintptr_t)frame, 1);
}
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern const char r1_lis_tap_disable_ring[36],r1_lis_tap_disable_sdk[28];
extern const char r1_lis_tap_enable_ring[52],r1_lis_tap_enable_sdk[48];
static uint32_t tap_log(const char *ring,const char *sdk)
{
 /* Each gate reloads the live mode, including the short-circuited second
  * read. Sensor errors do not skip either the following settings or logs. */
 if ((r1_structured_log_mode_get() & 1u) ||
     (r1_structured_log_mode_get() & 4u))
  (void)r1_structured_log_format(0x0c000000,ring,ring);
 if (r1_structured_log_mode_get() & 2u)
  nrf_log_frontend_std_0(0x001c0003,sdk);
 return 1;
}
uint32_t r1_lis2dw12_aux20_boundary(void)
{
 volatile uint8_t route=0;
 const stmdev_ctx_t *ctx=(const void *)&r1_lis_context;
 (void)lis2dw12_pin_int1_route_get(ctx,(void *)(uintptr_t)&route);
 route &= (uint8_t)~8u;
 (void)lis2dw12_pin_int1_route_set(ctx,(void *)(uintptr_t)&route);
 (void)lis2dw12_tap_detection_on_z_set(ctx,0);
 (void)lis2dw12_tap_detection_on_y_set(ctx,0);
 (void)lis2dw12_tap_detection_on_x_set(ctx,0);
 (void)lis2dw12_tap_mode_set(ctx,0);
 (void)lis2dw12_full_scale_set(ctx,2);
 (void)lis2dw12_data_rate_set(ctx,3);
 return tap_log(r1_lis_tap_disable_ring,r1_lis_tap_disable_sdk);
}
uint32_t r1_lis2dw12_aux16_boundary(void)
{
 volatile uint8_t route=0;
 const stmdev_ctx_t *ctx=(const void *)&r1_lis_context;
 (void)lis2dw12_tap_detection_on_z_set(ctx,1);
 (void)lis2dw12_tap_detection_on_y_set(ctx,1);
 (void)lis2dw12_tap_detection_on_x_set(ctx,1);
 (void)lis2dw12_tap_threshold_x_set(ctx,3);
 (void)lis2dw12_tap_threshold_y_set(ctx,3);
 (void)lis2dw12_tap_threshold_z_set(ctx,3);
 (void)lis2dw12_tap_dur_set(ctx,0);
 (void)lis2dw12_tap_quiet_set(ctx,0);
 (void)lis2dw12_tap_shock_set(ctx,0);
 (void)lis2dw12_tap_mode_set(ctx,1);
 (void)lis2dw12_pin_int1_route_get(ctx,(void *)(uintptr_t)&route);
 route |= 8u;
 (void)lis2dw12_pin_int1_route_set(ctx,(void *)(uintptr_t)&route);
 return tap_log(r1_lis_tap_enable_ring,r1_lis_tap_enable_sdk);
}
const char r1_lis_tap_disable_ring[36] __attribute__((section(".r1.lis.tap.disable_ring")))="[RING]LIS2DOC double tap disabled";
const char r1_lis_tap_disable_sdk[28] __attribute__((section(".r1.lis.tap.disable_sdk")))="LIS2DOC double tap disabled";
const char r1_lis_tap_enable_ring[52] __attribute__((section(".r1.lis.tap.enable_ring")))="[RING]LIS2DOC double tap enabled (ODR=400Hz, FS=2g)";
const char r1_lis_tap_enable_sdk[48] __attribute__((section(".r1.lis.tap.enable_sdk")))="LIS2DOC double tap enabled (ODR=400Hz, FS=2g)";
