/* Attributed ST adaptation: native saved-register byte is explicit.
BSD 3-Clause License

Copyright (c) 2019, STMicroelectronics
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

*/
#include <stdint.h>
#include "lis2dw12_reg.h"
int32_t lis2dw12_auto_increment_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_ctrl2_t *reg=(lis2dw12_ctrl2_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL2, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->if_add_inc = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_CTRL2, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_fifo_mode_set_body(const stmdev_ctx_t *ctx,
                               lis2dw12_fmode_t val, volatile uint8_t *frame)
{
  lis2dw12_fifo_ctrl_t *reg=(lis2dw12_fifo_ctrl_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_FIFO_CTRL, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->fmode = (uint8_t) val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_FIFO_CTRL, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_fifo_watermark_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_fifo_ctrl_t *reg=(lis2dw12_fifo_ctrl_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_FIFO_CTRL, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->fth = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_FIFO_CTRL, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_filter_bandwidth_set_body(const stmdev_ctx_t *ctx,
                                      lis2dw12_bw_filt_t val, volatile uint8_t *frame)
{
  lis2dw12_ctrl6_t *reg=(lis2dw12_ctrl6_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL6, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->bw_filt = (uint8_t) val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_CTRL6, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_full_scale_set_body(const stmdev_ctx_t *ctx, lis2dw12_fs_t val, volatile uint8_t *frame)
{
  lis2dw12_ctrl6_t *reg=(lis2dw12_ctrl6_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL6, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->fs = (uint8_t) val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_CTRL6, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_reset_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_ctrl2_t *reg=(lis2dw12_ctrl2_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL2, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->soft_reset = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_CTRL2, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_detection_on_z_set_body(const stmdev_ctx_t *ctx,
                                        uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_tap_ths_z_t *reg=(lis2dw12_tap_ths_z_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_TAP_THS_Z, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->tap_z_en = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_TAP_THS_Z, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_detection_on_y_set_body(const stmdev_ctx_t *ctx,
                                        uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_tap_ths_z_t *reg=(lis2dw12_tap_ths_z_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_TAP_THS_Z, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->tap_y_en = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_TAP_THS_Z, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_detection_on_x_set_body(const stmdev_ctx_t *ctx,
                                        uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_tap_ths_z_t *reg=(lis2dw12_tap_ths_z_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_TAP_THS_Z, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->tap_x_en = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_TAP_THS_Z, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_dur_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_int_dur_t *reg=(lis2dw12_int_dur_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_INT_DUR, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->latency = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_INT_DUR, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_mode_set_body(const stmdev_ctx_t *ctx,
                              lis2dw12_single_double_tap_t val, volatile uint8_t *frame)
{
  lis2dw12_wake_up_ths_t *reg=(lis2dw12_wake_up_ths_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_WAKE_UP_THS, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->single_double_tap = (uint8_t) val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_WAKE_UP_THS, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_quiet_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_int_dur_t *reg=(lis2dw12_int_dur_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_INT_DUR, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->quiet = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_INT_DUR, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_shock_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_int_dur_t *reg=(lis2dw12_int_dur_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_INT_DUR, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->shock = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_INT_DUR, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_threshold_x_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_tap_ths_x_t *reg=(lis2dw12_tap_ths_x_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_TAP_THS_X, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->tap_thsx = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_TAP_THS_X, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_threshold_y_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_tap_ths_y_t *reg=(lis2dw12_tap_ths_y_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_TAP_THS_Y, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->tap_thsy = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_TAP_THS_Y, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_tap_threshold_z_set_body(const stmdev_ctx_t *ctx, uint8_t val, volatile uint8_t *frame)
{
  lis2dw12_tap_ths_z_t *reg=(lis2dw12_tap_ths_z_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_TAP_THS_Z, (uint8_t *)reg, 1);

  if (ret == 0)
  {
    reg->tap_thsz = val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_TAP_THS_Z, (uint8_t *)reg, 1);
  }

  return ret;
}
int32_t lis2dw12_reset_get_body(const stmdev_ctx_t *ctx, uint8_t *val, volatile uint8_t *frame)
{
  lis2dw12_ctrl2_t *reg=(lis2dw12_ctrl2_t *)(uintptr_t)frame;
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL2, (uint8_t *)reg, 1);
  *val = reg->soft_reset;

  return ret;
}
