/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_GX8002_ANALOG_H
#define OPEN_CFW_GX8002_ANALOG_H
#include <stdint.h>

int gx_analog_set_pga_itrim(uint32_t itrim);
int gx_analog_set_pga_bypass(uint32_t bypass);
int gx_analog_set_pga_enable(uint32_t enable);
int gx_analog_set_adc_sample_clk_sel(uint32_t select);
int gx_analog_set_adc_out_at_clk(uint32_t clock);
int gx_analog_set_adc_in_sel(uint32_t select);
int gx_analog_set_adc_rstn(uint32_t reset_n);
#endif
