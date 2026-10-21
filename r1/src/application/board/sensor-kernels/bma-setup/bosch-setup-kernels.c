/* Attributed Bosch validator and factored register updates.
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
int8_t r1_bma_validate_accel_parameters(uint8_t odr, uint8_t bandwidth, uint8_t perf_mode);
static int8_t r1_bma_validate_bandwidth_perfmode(uint8_t bandwidth, uint8_t perf_mode);
static int8_t r1_bma_validate_odr(uint8_t odr);
static int8_t r1_bma_validate_bandwidth_odr(uint8_t bandwidth, uint8_t odr);
int8_t r1_bma_validate_accel_parameters(uint8_t odr, uint8_t bandwidth, uint8_t perf_mode)
{
    int8_t rslt;

    /* Check bandwidth and perf_mode combinations */
    rslt = r1_bma_validate_bandwidth_perfmode(bandwidth, perf_mode);

    if (rslt == BMA4_OK)
    {
        /* Check ODR validity */
        rslt = r1_bma_validate_odr(odr);
    }

    if (rslt == BMA4_OK)
    {
        /* Validate ODR and bandwidth combinations when perf_mode = BMA4_CIC_AVG_MODE */
        if (perf_mode == BMA4_CIC_AVG_MODE)
        {
            rslt = r1_bma_validate_bandwidth_odr(bandwidth, odr);
        }
    }

    return rslt;

}
static int8_t r1_bma_validate_bandwidth_perfmode(uint8_t bandwidth, uint8_t perf_mode)
{
    int8_t rslt = BMA4_OK;

    if (perf_mode == BMA4_CONTINUOUS_MODE)
    {
        if (bandwidth > BMA4_ACCEL_NORMAL_AVG4)
        {
            /* Invalid bandwidth error for continuous mode */
            rslt = BMA4_E_OUT_OF_RANGE;
        }
    }
    else if (perf_mode == BMA4_CIC_AVG_MODE)
    {
        if (bandwidth > BMA4_ACCEL_RES_AVG128)
        {
            /* Invalid bandwidth error for CIC avg. mode */
            rslt = BMA4_E_OUT_OF_RANGE;
        }
    }
    else
    {
        rslt = BMA4_E_OUT_OF_RANGE;
    }

    return rslt;
}
static int8_t r1_bma_validate_odr(uint8_t odr)
{
    int8_t rslt = BMA4_OK;

    if ((odr < BMA4_OUTPUT_DATA_RATE_0_78HZ) || (odr > BMA4_OUTPUT_DATA_RATE_1600HZ))
    {
        /* If odr is not valid return error */
        rslt = BMA4_E_OUT_OF_RANGE;
    }

    return rslt;
}
static int8_t r1_bma_validate_bandwidth_odr(uint8_t bandwidth, uint8_t odr)
{
    int8_t rslt = BMA4_OK;
    uint8_t index;

    /*
     * Array contains ODR values
     * From BMA4_OUTPUT_DATA_RATE_0_78HZ (value = 1)
     * To BMA4_OUTPUT_DATA_RATE_400HZ (value = 10)
     */
    uint8_t accel_odr[10] = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

    /*
     * Array contains valid bandwidth values for each ODR
     */
    uint8_t valid_bw[10] = { 7, 7, 7, 7, 6, 5, 4, 3, 2, 1 };

    /*
     * For ODR - 800Hz and 1600Hz, none of the bandwidth is applicable
     */
    if ((odr == BMA4_OUTPUT_DATA_RATE_800HZ) || (odr == BMA4_OUTPUT_DATA_RATE_1600HZ))
    {
        rslt = BMA4_E_AVG_MODE_INVALID_CONF;
    }

    /*
     * Maximum valid bandwidth value for accel_odr[index] is the
     * corresponding value in valid_bw[index]
     */
    for (index = 0; index < 10; index++)
    {
        if (odr == accel_odr[index])
        {
            if (bandwidth > valid_bw[index])
            {
                rslt = BMA4_E_AVG_MODE_INVALID_CONF;
            }
        }
    }

    return rslt;
}
uint32_t r1_bma_accel_enable_byte(uint32_t byte,uint32_t val) {uint8_t data=(uint8_t)byte,accel_en=(uint8_t)val;data = BMA4_SET_BITSLICE(data, BMA4_ACCEL_ENABLE, accel_en); return data;}
uint32_t r1_bma_fifo_config_bytes(uint32_t packed,uint32_t config,uint32_t enable) {uint8_t data[2]={(uint8_t)packed,(uint8_t)(packed>>8)};uint8_t fifo_config_0=config&BMA4_FIFO_CONFIG_0_MASK;
            if (fifo_config_0 > 0)
            {
                if (enable == TRUE)
                {
                    data[0] = data[0] | fifo_config_0;
                }
                else
                {
                    data[0] = data[0] & (~fifo_config_0);
                }
            }

            if (enable == TRUE)
            {
                data[1] = data[1] | (config & BMA4_FIFO_CONFIG_1_MASK);
            }
            else
            {
                data[1] = data[1] & (~(config & BMA4_FIFO_CONFIG_1_MASK));
            }

return data[0]|((uint32_t)data[1]<<8);}
