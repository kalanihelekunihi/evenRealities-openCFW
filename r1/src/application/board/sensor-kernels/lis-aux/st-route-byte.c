/* Attributed ST route-enable condition and assignments, factored pure.
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
uint32_t r1_lis_int1_route_byte(uint32_t ctrl4,uint32_t ctrl5,uint32_t ctrl7) {
union {uint8_t byte;lis2dw12_ctrl4_int1_pad_ctrl_t reg;}u4;
union {uint8_t byte;lis2dw12_ctrl5_int2_pad_ctrl_t reg;}u5;
union {uint8_t byte;lis2dw12_ctrl_reg7_t reg;}u7;
_Static_assert(sizeof(u4)==1 && sizeof(u5)==1 && sizeof(u7)==1,"native bytes");
u4.byte=(uint8_t)ctrl4;u5.byte=(uint8_t)ctrl5;u7.byte=(uint8_t)ctrl7;
    if ((u4.reg.int1_tap |
         u4.reg.int1_ff |
         u4.reg.int1_wu |
         u4.reg.int1_single_tap |
         u4.reg.int1_6d |
         u5.reg.int2_sleep_state |
         u5.reg.int2_sleep_chg) != PROPERTY_DISABLE)
    {
      u7.reg.interrupts_enable = PROPERTY_ENABLE;
    }

    else
    {
      u7.reg.interrupts_enable = PROPERTY_DISABLE;
    }

return u7.byte;
}
