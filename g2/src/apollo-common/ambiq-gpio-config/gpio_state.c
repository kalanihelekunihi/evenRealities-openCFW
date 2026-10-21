//*****************************************************************************
//
// Copyright (c) 2025, Ambiq Micro, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
// this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
// contributors may be used to endorse or promote products derived from this
// software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//
// This is part of revision release_sdk5p1p0-366b80e084 of the AmbiqSuite Development Package.
//
//*****************************************************************************

#include "gpio_config_compat.h"

uint32_t
am_hal_gpio_state_write(uint32_t ui32GpioNum, am_hal_gpio_write_type_e eWriteType)
{
    //
    // Find the correct register to read based on the read type input. Each of
    // these registers map exactly one bit to each pin, so the calculation for
    // which register to use is simple.
    //
    switch (eWriteType)
    {
        case AM_HAL_GPIO_OUTPUT_CLEAR:
            am_hal_gpio_output_clear(ui32GpioNum);
            break;

        case AM_HAL_GPIO_OUTPUT_SET:
            am_hal_gpio_output_set(ui32GpioNum);
            break;

        case AM_HAL_GPIO_OUTPUT_TOGGLE:
            am_hal_gpio_output_toggle(ui32GpioNum);
            break;

        case AM_HAL_GPIO_OUTPUT_TRISTATE_OUTPUT_DIS:
            am_hal_gpio_output_tristate_output_dis(ui32GpioNum);
            break;

        case AM_HAL_GPIO_OUTPUT_TRISTATE_OUTPUT_EN:
            am_hal_gpio_output_tristate_output_en(ui32GpioNum);
            break;

        case AM_HAL_GPIO_OUTPUT_TRISTATE_OUTPUT_TOG:
            am_hal_gpio_output_tristate_output_tog(ui32GpioNum);
            break;
    }

    return AM_HAL_STATUS_SUCCESS;

}

/* Recovered raw ARM entry semantics: the stock callee truncates r1 to a byte.
 * The public byte-sized interface requires ABI-valid zero extension; this
 * adapter makes arbitrary raw register inputs well-defined for comparison.
 */
uint32_t opencfw_gpio_state_write_raw(uint32_t pin, uint32_t operation)
{
    return am_hal_gpio_state_write(pin, (am_hal_gpio_write_type_e)operation);
}
