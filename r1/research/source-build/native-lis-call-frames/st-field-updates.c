/* Attributed ST assignments factored into pure byte updates.
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
uint32_t r1_field_lis2dw12_block_data_update_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_ctrl2_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.bdu = val; return u.byte; }
uint32_t r1_field_lis2dw12_fifo_mode_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_fifo_ctrl_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.fmode = (uint8_t) val; return u.byte; }
uint32_t r1_field_lis2dw12_fifo_watermark_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_fifo_ctrl_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.fth = val; return u.byte; }
uint32_t r1_field_lis2dw12_filter_bandwidth_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_ctrl6_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.bw_filt = (uint8_t) val; return u.byte; }
uint32_t r1_field_lis2dw12_full_scale_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_ctrl6_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.fs = (uint8_t) val; return u.byte; }
uint32_t r1_field_lis2dw12_reset_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_ctrl2_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.soft_reset = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_detection_on_x_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_tap_ths_z_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.tap_x_en = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_detection_on_y_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_tap_ths_z_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.tap_y_en = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_detection_on_z_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_tap_ths_z_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.tap_z_en = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_dur_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_int_dur_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.latency = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_mode_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_wake_up_ths_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.single_double_tap = (uint8_t) val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_quiet_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_int_dur_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.quiet = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_shock_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_int_dur_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.shock = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_threshold_x_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_tap_ths_x_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.tap_thsx = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_threshold_y_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_tap_ths_y_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.tap_thsy = val; return u.byte; }
uint32_t r1_field_lis2dw12_tap_threshold_z_set_reg(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_tap_ths_z_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.tap_thsz = val; return u.byte; }
uint32_t r1_field_lis2dw12_data_rate_set_ctrl1(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_ctrl1_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.odr = (uint8_t) val; return u.byte; }
uint32_t r1_field_lis2dw12_data_rate_set_ctrl3(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_ctrl3_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.slp_mode = ((uint8_t) val & 0x30U) >> 4; return u.byte; }
uint32_t r1_field_lis2dw12_filter_path_set_ctrl6(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_ctrl6_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.fds = ((uint8_t) val & 0x10U) >> 4; return u.byte; }
uint32_t r1_field_lis2dw12_filter_path_set_ctrl_reg7(uint32_t byte,uint32_t val) { union {uint8_t byte; lis2dw12_ctrl_reg7_t reg;} u; _Static_assert(sizeof(u)==1,"native register byte"); u.byte=(uint8_t)byte; u.reg.usr_off_on_out = (uint8_t) val & 0x01U; return u.byte; }
uint32_t r1_native_power_first(uint32_t b,uint32_t v) {return (b&0xf1u)|((v&1u)<<3)|(v&6u);}
uint32_t r1_native_power_second(uint32_t b,uint32_t v) {return (b&0xfbu)|((v&8u)>>1);}
uint32_t r1_native_reg17_update(uint32_t b) {return b|0x40u;}
