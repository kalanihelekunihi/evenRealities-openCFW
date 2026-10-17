/* Attributed Bosch pure updates factored between native transport calls.
Copyright (c) 2024 Bosch Sensortec GmbH. All rights reserved.

BSD-3-Clause

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*/
#include "bma4.h"
uint32_t r1_bma_power_update_byte(uint32_t byte,uint32_t val) {uint8_t data=(uint8_t)byte; uint8_t adv_pwr_save=(uint8_t)val; data = BMA4_SET_BITS_POS_0(data, BMA4_ADVANCE_POWER_SAVE, adv_pwr_save); return data;}
uint32_t r1_bma_feature_address_bytes(uint32_t lo,uint32_t hi,const struct bma4_dev *dev) {uint8_t asic_lsb=(uint8_t)lo,asic_msb=(uint8_t)hi;uint16_t asic_addr;
asic_addr = (asic_msb << 4) | (asic_lsb & 0x0F);
asic_addr = asic_addr + (dev->read_write_len / 2);
asic_lsb = asic_addr & 0x0F;
asic_msb = (uint8_t)(asic_addr >> 4);
return asic_lsb|((uint32_t)asic_msb<<8);}
