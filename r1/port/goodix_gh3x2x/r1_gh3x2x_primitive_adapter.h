#ifndef R1_GH3X2X_PRIMITIVE_ADAPTER_H
#define R1_GH3X2X_PRIMITIVE_ADAPTER_H

/*
 * Checked views from the recovered, provider-independent GH3X2X input
 * record into the transparent Goodix HR, HRV, and SpO2 contracts.
 * The returned pointers borrow storage from `input`; callers must keep it
 * alive and mutable for the duration of the primitive call.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "goodix_primitives/goodix_primitives.h"
#include "r1_gh3x2x_algo_bridge.h"

bool r1_gh3x2x_algo_bind_hr_primitive_input(
    r1_gh3x2x_algo_input *input, const uint8_t *filter_code,
    size_t filter_code_count,
    goodix_primitives_hba_process_input *primitive);

bool r1_gh3x2x_algo_bind_hrv_primitive_input(
    r1_gh3x2x_algo_input *input,
    goodix_primitives_hrv_process_input *primitive);

bool r1_gh3x2x_algo_bind_spo2_primitive_input(
    r1_gh3x2x_algo_input *input,
    goodix_primitives_spo2_calc_input *primitive);

#endif
