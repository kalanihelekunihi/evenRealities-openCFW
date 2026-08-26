/*
 *
 * Copyright (c) [2020] by InvenSense, Inc.
 * 
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 * SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
 * OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 */

#include "sif_feature_extract_ir.h"
#include <string.h>
#include <stdint.h>

#define FLT_HIST_NUM ((MAX_FLT_COEF >> 1))

/**
 * @brief Vector Multiplication and Accumulation operation using MAU .
 * @param[in] vector_1_data: pointer to the data of the M vector 1 (with M the number of vector pairs(vect1 and 2))
 * @param[in] vector_2_data: pointer to the data of the M vector 2
 * @param[out] result: pointer to the data of the M results
 * @param[in] vector_length: N : Numbers of points in vectors
 **/
void sif_feature_math_mac(int32_t *vector_1_data, int32_t *vector_2_data, int64_t *result,
                          uint16_t vector_length)
{
	int32_t i;
	int64_t mau_accumulator = 0;

	for (i = 0; i < vector_length; i++)
		mau_accumulator += ((int64_t)vector_1_data[i]) * ((int64_t)vector_2_data[i]);
	*(int64_t *)result = mau_accumulator;
}

// common config initialization
void SIF_CommonConfig_Init(config_common_t *config, int32_t win_size, int32_t tconfigs_num)
{
	config->win_size     = win_size;
	config->win_size_m   = win_size - (win_size % FLT_HIST_NUM);
	config->tconfigs_num = tconfigs_num;
}

// temporal config initialization
void SIF_TemporalConfig_Init(config_time_t *config, int32_t inv_win_size, int32_t hyst_thr_q16,
                             int32_t min_peak_dist, int32_t min_peak_height)
{
	config->inv_win_size    = inv_win_size;
	config->hyst_thr_q16    = hyst_thr_q16;
	config->min_peak_dist   = min_peak_dist;
	config->min_peak_height = min_peak_height;
}

// filter initialization
void SIF_Filter_Init(filter_state_t *filter, int32_t num_coef, const int32_t FiltBnA_Q28[])
{
	filter->num_coef = num_coef;
	// Fill in B and A coefficients
	memcpy(filter->BnA_q28, FiltBnA_Q28, num_coef * sizeof(int32_t));
	memset(filter->xy_q24, 0, num_coef * sizeof(int32_t));
	filter->initialization = 0;

	int64_t out_data;
	int64_t Q28 = 1 << 28;
	int64_t delta;
	int32_t ones_table_8[8] = { 1, 1, 1, 1, 1, 1, 1, 1 };

	// sum last 8 elements (coefficients)
	sif_feature_math_mac((filter->BnA_q28 + 1), ones_table_8, &out_data, filter->num_coef - 1);

	// identify type of filter based on information provided by coefficients sum
	if (out_data == 0) {
		filter->filter_type = NO_FILTER;
	} else {
		out_data += filter->BnA_q28[0];
		delta = out_data - Q28;
		if ((delta <= 3) && (delta >= -3)) {
			filter->filter_type = LOW_PASS_FILTER;
		} else {
			filter->filter_type = HIGH_OR_BAND_PASS_FILTER;
		}
	}
}

// filter states reset
void SIF_Filter_ResetState(filter_state_t *filter)
{
	memset(filter->xy_q24, 0, filter->num_coef * sizeof(int32_t));
	filter->initialization = 0; // flag to keep track of initialization state
}

// time statistics reset
int32_t SIF_TimeStatistics_ResetState(statistics_state_t *sstate, int32_t *pmean)
{
	memset(sstate, 0, sizeof(statistics_state_t));
	if (pmean) {
		sstate->prv_mean_q16 = *pmean;
	}
	return 0;
}

// features reset (count)
int32_t SIF_Features_ResetState(features_state_t *state)
{
	state->tcount_ = 0;
	return 0;
};
