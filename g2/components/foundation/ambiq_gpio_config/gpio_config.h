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

#ifndef OPENCFW_GPIO_CONFIG_H
#define OPENCFW_GPIO_CONFIG_H
#include <stdint.h>
typedef struct
{
    union
    {
        volatile uint32_t cfg;

        struct
        {
            uint32_t uFuncSel        : 4;   // [3:0]
            uint32_t eGPInput        : 1;   // [4:4]
            uint32_t eGPRdZero       : 1;   // [5:5]
            uint32_t eIntDir         : 2;   // [7:6]
            uint32_t eGPOutCfg       : 2;   // [9:8]
            uint32_t eDriveStrength  : 3;   // [12:10]  // See information and details above
            uint32_t ePullup         : 3;   // [15:13]
            uint32_t uNCE            : 6;   // [21:16]
            uint32_t eCEpol          : 1;   // [22:22]
            uint32_t uRsvd_0         : 2;   // [24:23]
            uint32_t ePowerSw        : 1;   // [25:25]  // Select pads only, otherwise reserved
            uint32_t eForceInputEn   : 1;   // [26:26]
            uint32_t eForceOutputEn  : 1;   // [27:27]
            uint32_t uRsvd_1         : 4;   // [31:28]
        } cfg_b;
    } GP;
} am_hal_gpio_pincfg_t;
/* Recovered callable ABI: config is passed by value in ARM r1.
 * Getter output remains caller-owned. GPIO register cells are volatile.
 * Setter supports 224 logical indices; this is not a physical-pad inventory.
 * Valid setter writes unlock/config/relock under saved/restored PRIMASK.
 * Physical pin readiness, peripheral clock and NVIC are outside this API.
 */
uint32_t am_hal_gpio_pinconfig_get(uint32_t pin, am_hal_gpio_pincfg_t *config);
uint32_t am_hal_gpio_pinconfig(uint32_t pin, am_hal_gpio_pincfg_t config);
/* Stock operation byte ABI; constants retain pinned upstream ordering.
 * State writes mask bank=(pin>>5)&7 and bit=pin&31; no pin range check.
 * Application callers must validate their board pin before calling.
 */
typedef uint8_t am_hal_gpio_write_type_e;
enum {
    AM_HAL_GPIO_OUTPUT_CLEAR,
    AM_HAL_GPIO_OUTPUT_SET,
    AM_HAL_GPIO_OUTPUT_TOGGLE,
    AM_HAL_GPIO_OUTPUT_TRISTATE_OUTPUT_DIS,    // Disable output, i.e. Hi-Z
    AM_HAL_GPIO_OUTPUT_TRISTATE_OUTPUT_EN,     // Enable output
    AM_HAL_GPIO_OUTPUT_TRISTATE_OUTPUT_TOG
};
uint32_t am_hal_gpio_state_write(uint32_t pin, am_hal_gpio_write_type_e operation);
uint32_t opencfw_gpio_state_write_raw(uint32_t pin, uint32_t raw_operation);
/* Reconstructed stock void board helper: clear pin93 then configure pin138.
 * Return statuses are ignored by stock; no electrical readiness guarantee.
 */
void opencfw_radio_gpio_idle_pins(void);
extern const volatile am_hal_gpio_pincfg_t opencfw_radio_pin138_idle_config;

#endif
