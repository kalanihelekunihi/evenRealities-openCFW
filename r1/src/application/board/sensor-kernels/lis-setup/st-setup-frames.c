/* Attributed ST frame adaptation.
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
int32_t lis2dw12_data_rate_set_body(const stmdev_ctx_t *ctx, lis2dw12_odr_t val, volatile uint8_t *frame)
{
  lis2dw12_ctrl1_t *ctrl1=(lis2dw12_ctrl1_t *)(uintptr_t)(frame+0);
  lis2dw12_ctrl3_t *ctrl3=(lis2dw12_ctrl3_t *)(uintptr_t)(frame+4);
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL1, (uint8_t *)ctrl1, 1);

  if (ret == 0)
  {
    ctrl1->odr = (uint8_t) val;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_CTRL1, (uint8_t *)ctrl1, 1);
  }

  if (ret == 0)
  {
    ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL3, (uint8_t *)ctrl3, 1);
  }

  if (ret == 0)
  {
    ctrl3->slp_mode = ((uint8_t) val & 0x30U) >> 4;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_CTRL3, (uint8_t *)ctrl3, 1);
  }

  return ret;
}
int32_t lis2dw12_filter_path_set_body(const stmdev_ctx_t *ctx,
                                 lis2dw12_fds_t val, volatile uint8_t *frame)
{
  lis2dw12_ctrl6_t *ctrl6=(lis2dw12_ctrl6_t *)(uintptr_t)(frame+0);
  lis2dw12_ctrl_reg7_t *ctrl_reg7=(lis2dw12_ctrl_reg7_t *)(uintptr_t)(frame+4);
  int32_t ret;

  ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL6, (uint8_t *)ctrl6, 1);

  if (ret == 0)
  {
    ctrl6->fds = ((uint8_t) val & 0x10U) >> 4;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_CTRL6, (uint8_t *)ctrl6, 1);
  }

  if (ret == 0)
  {
    ret = lis2dw12_read_reg(ctx, LIS2DW12_CTRL_REG7,
                            (uint8_t *)ctrl_reg7, 1);
  }

  if (ret == 0)
  {
    ctrl_reg7->usr_off_on_out = (uint8_t) val & 0x01U;
    ret = lis2dw12_write_reg(ctx, LIS2DW12_CTRL_REG7,
                             (uint8_t *)ctrl_reg7, 1);
  }

  return ret;
}
