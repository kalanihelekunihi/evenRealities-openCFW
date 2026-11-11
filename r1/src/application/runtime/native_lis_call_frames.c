/* Ordinary C register APIs. Unwritten scratch bytes start at zero. */
#include <stdint.h>
#include <stddef.h>
#include "lis2dw12_reg.h"
struct r1_lis_byte_field {
 uint32_t reg;
 uint32_t (*update)(uint32_t, uint32_t);
};
_Static_assert(sizeof(struct r1_lis_byte_field)==8 &&
 offsetof(struct r1_lis_byte_field,update)==4, "native field descriptor");
__attribute__((used,noinline)) uint32_t r1_lis_byte_set_body(const void *ctx,
 uint32_t value, volatile uint8_t *frame, const struct r1_lis_byte_field *field)
{
 uint32_t status = (uint32_t)lis2dw12_read_reg(ctx, (uint8_t)field->reg,
                                            (uint8_t *)(uintptr_t)frame, 1);
 if (status != 0)
  return status;
 frame[0] = (uint8_t)field->update(frame[0], value);
 return (uint32_t)lis2dw12_write_reg(ctx, (uint8_t)field->reg,
                                   (uint8_t *)(uintptr_t)frame, 1);
}
#define BYTE_SETTER(name,type,regno,operation) \
 extern uint32_t operation(uint32_t, uint32_t); \
 static const struct r1_lis_byte_field field_##name __attribute__((used)) = {regno,operation}; \
 int32_t name(const stmdev_ctx_t *ctx,type value) { \
  uint8_t byte=0; \
  return (int32_t)r1_lis_byte_set_body(ctx,(uint32_t)value,&byte,&field_##name); \
 }
BYTE_SETTER(lis2dw12_block_data_update_set,uint8_t, 33, r1_field_lis2dw12_block_data_update_set_reg)
BYTE_SETTER(lis2dw12_fifo_mode_set,lis2dw12_fmode_t, 46, r1_field_lis2dw12_fifo_mode_set_reg)
BYTE_SETTER(lis2dw12_fifo_watermark_set,uint8_t, 46, r1_field_lis2dw12_fifo_watermark_set_reg)
BYTE_SETTER(lis2dw12_filter_bandwidth_set,lis2dw12_bw_filt_t, 37, r1_field_lis2dw12_filter_bandwidth_set_reg)
BYTE_SETTER(lis2dw12_full_scale_set,lis2dw12_fs_t, 37, r1_field_lis2dw12_full_scale_set_reg)
BYTE_SETTER(lis2dw12_reset_set,uint8_t, 33, r1_field_lis2dw12_reset_set_reg)
BYTE_SETTER(lis2dw12_tap_detection_on_x_set,uint8_t, 50, r1_field_lis2dw12_tap_detection_on_x_set_reg)
BYTE_SETTER(lis2dw12_tap_detection_on_y_set,uint8_t, 50, r1_field_lis2dw12_tap_detection_on_y_set_reg)
BYTE_SETTER(lis2dw12_tap_detection_on_z_set,uint8_t, 50, r1_field_lis2dw12_tap_detection_on_z_set_reg)
BYTE_SETTER(lis2dw12_tap_dur_set,uint8_t, 51, r1_field_lis2dw12_tap_dur_set_reg)
BYTE_SETTER(lis2dw12_tap_mode_set,lis2dw12_single_double_tap_t, 52, r1_field_lis2dw12_tap_mode_set_reg)
BYTE_SETTER(lis2dw12_tap_quiet_set,uint8_t, 51, r1_field_lis2dw12_tap_quiet_set_reg)
BYTE_SETTER(lis2dw12_tap_shock_set,uint8_t, 51, r1_field_lis2dw12_tap_shock_set_reg)
BYTE_SETTER(lis2dw12_tap_threshold_x_set,uint8_t, 48, r1_field_lis2dw12_tap_threshold_x_set_reg)
BYTE_SETTER(lis2dw12_tap_threshold_y_set,uint8_t, 49, r1_field_lis2dw12_tap_threshold_y_set_reg)
BYTE_SETTER(lis2dw12_tap_threshold_z_set,uint8_t, 50, r1_field_lis2dw12_tap_threshold_z_set_reg)
#undef BYTE_SETTER
struct r1_lis_byte_extract { uint32_t reg, shift, mask; };
__attribute__((used,noinline)) uint32_t r1_lis_byte_get_body(const void *ctx,
 volatile uint8_t *destination, const volatile uint8_t *frame,
 const struct r1_lis_byte_extract *field)
{
 uint32_t status = (uint32_t)lis2dw12_read_reg(ctx, (uint8_t)field->reg,
                                            (uint8_t *)(uintptr_t)frame, 1);
 uint32_t value = (frame[0] >> field->shift) & field->mask;
 *destination = (uint8_t)value;
 return status;
}
#define BYTE_GETTER(name,regno,shiftno,maskno) \
 static const struct r1_lis_byte_extract extract_##name __attribute__((used)) = {regno,shiftno,maskno}; \
 int32_t name(const stmdev_ctx_t *ctx,uint8_t *destination) { \
  uint8_t byte=0; \
  return (int32_t)r1_lis_byte_get_body(ctx,destination,&byte,&extract_##name); \
 }
BYTE_GETTER(lis2dw12_reset_get, 0x21, 6, 1)
BYTE_GETTER(lis2dw12_fifo_data_level_get, 0x2f, 0, 0x3f)
#undef BYTE_GETTER
extern int32_t lis2dw12_data_rate_set_body(const stmdev_ctx_t *,lis2dw12_odr_t,volatile uint8_t *);
extern int32_t lis2dw12_filter_path_set_body(const stmdev_ctx_t *,lis2dw12_fds_t,volatile uint8_t *);
extern uint32_t r1_lis_power_body(const void *,uint32_t,volatile uint8_t *);
extern uint32_t r1_lis_reg17_body(const void *,uint32_t,volatile uint8_t *);
int32_t lis2dw12_data_rate_set(const stmdev_ctx_t *ctx,lis2dw12_odr_t value)
{
 volatile uint8_t bytes[8]={0};
 return lis2dw12_data_rate_set_body(ctx,value,bytes);
}
int32_t lis2dw12_filter_path_set(const stmdev_ctx_t *ctx,lis2dw12_fds_t value)
{
 volatile uint8_t bytes[8]={0};
 return lis2dw12_filter_path_set_body(ctx,value,bytes);
}
uint32_t r1_lis_native_power_mode_set(const void *ctx,uint32_t value)
{
 volatile uint8_t bytes[8]={0};
 return r1_lis_power_body(ctx,value,bytes);
}
uint32_t r1_lis_reg17_bit6_enable(const void *ctx)
{
 volatile uint8_t byte=0;
 return r1_lis_reg17_body(ctx,0,&byte);
}
