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

#ifndef FEATURE_EXTRACT_IR_
#define FEATURE_EXTRACT_IR_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

#define ARRAY_SIZE(x) (sizeof((x)) / sizeof((x[0])))
#define MAX_FLT_COEF  (9)
#define NUM_TIME_FEAS (10) // Number of unique time features

#define ACC_T_FILTERS_NUM_MAX                                                                      \
	(4) // max number of unique filters used in for time signal preprocessing
#define ACC_T_CONFIG_NUM_MAX                                                                       \
	(ACC_T_FILTERS_NUM_MAX *                                                                       \
	 3) // max number of time configuration blocks (combination of axis+filter)
#define ACC_T_NUM_FEAS_TOTAL_MAX                                                                   \
	(ACC_T_CONFIG_NUM_MAX * NUM_TIME_FEAS) // max number of enabled time-domain features

#define NO_FILTER                (0)
#define LOW_PASS_FILTER          (1)
#define HIGH_OR_BAND_PASS_FILTER (2)

typedef struct {
	int32_t sum[3]; /*!< 3-axis accumulator */

	uint8_t counter;
	uint8_t counter_log2;
	uint8_t
	    downsample_factor; /*!< Number of points of downsampling possible values 1 (default), 2, 4, 8, 16, 32, 64 */

	uint32_t data_sample_q16_downsampled[3];
	uint32_t status;
} sif_AvgDownsampler;

/** \defgroup FeatureExtractionFxp Feature Extraction from data signals
*   \brief This module includes the structures and functions to perform pre-processing and feature extraction on data signals in fixed point.
*   \ingroup FeatureExtractionFxp
*/

typedef struct {
	int32_t BnA_q28
	    [MAX_FLT_COEF]; /*!< Coefficient array in Q28 populated with [b_q28(1), b_q28(2), b_q28(3), b_q28(4), b_q28(5), -a_q28(1), -a_q28(2), , -a_q28(3), -a_q28]  with b_q28, a_q28 being the num and den coefficients of the filter in q28 fxp format.*/
	int32_t xy_q24[MAX_FLT_COEF]; /*!< Filter buffer with input/output data history. */
	uint8_t num_coef;
	uint8_t initialization; /*!< initialization flag for internal states of filters */
	uint8_t filter_type; /*!< Filter type (No filter, LPF, or BPF-HPF)*/
} filter_state_t; ///< \struct filter_state_t <><> \brief Filter state strcuture with filter coefficients and buffer. \ingroup FeatureExtractionFxp

typedef struct {
	int32_t  inv_win_size; /*!< inverse of window size */
	int32_t  hyst_thr_q16; /*!< hyst thresh in Q16 */
	int32_t  min_peak_dist; /*!< min peakdistance */
	int32_t  min_peak_height; /*!< min peak height */
	uint32_t acc_odr_us;
	uint32_t sif_pdr_us;
} config_time_t; ///< \struct config_time_t <><> \brief Time configuration structure including information for time-domain feature extraction. \ingroup FeatureExtractionFxp

typedef struct {
	int32_t win_size; /*!< window size in number of samples */
	int32_t win_size_m; /*!< window size in number of samples as multiple of filter output history*/
	int32_t
	    tconfigs_num; /*!< number of time configs i.e. the number of different filter/axis combinations*/
} config_common_t; ///< \struct config_common <><> \brief Common configuration structure including general settings for feature extraction. \ingroup FeatureExtractionFxp

typedef struct {
	config_common_t cconfig;
	config_time_t   tconfig;
	int32_t         tcount_;
} features_state_t; ///< \struct features_state_t <><> \brief Features state structure including all data and settings for feature extraction. \ingroup FeatureExtractionFxp

typedef struct {
	int32_t prv_mean_q16; /*!< previous mean value to be used for mean cross rate */
	int32_t sum_q16; /*!< sum representing marginal mean */
	int32_t ssum_q16; /*!< square sum */
	int32_t min_q16; /*!< minimum */
	int32_t max_q16; /*!< maximum */
	int32_t mcr; /*!< mean cross rate */
	int32_t pos_mcr; /*!< positive mean cross rate */
	int32_t neg_mcr; /*!< positive mean cross rate */
	int16_t en_pos_cross; /*!< positive cross flag */
	int16_t en_neg_cross; /*!< negative cross flag */

	/*peaks states*/
	int32_t xp[2];
	int32_t xn[2];
	int32_t prev_pp_age;
	int32_t prev_np_age;
	int32_t prev_pp;
	int32_t prev_np;
	int32_t num_peaks;
	int32_t num_npeaks;
	int32_t num_ppeaks;

} statistics_state_t; ///< \struct statistics_state_t <><> \brief Statistics state structure including all intermediate data for time-domain feature extraction. \ingroup FeatureExtractionFxp

typedef struct {
	int32_t            init;
	sif_AvgDownsampler acc_downsampler;
	int32_t            update_all_chunks;
	int32_t            data_sample_q16[3];
	features_state_t   feas_state;
	filter_state_t     filterTime[ACC_T_CONFIG_NUM_MAX];
	statistics_state_t statistics_state[ACC_T_CONFIG_NUM_MAX];
	int32_t            feas[ACC_T_NUM_FEAS_TOTAL_MAX];
} feature_extract_t; ///< \struct feature_extract_t <><> \brief Features extract structure including feas_state, filter_state, statistics_state, and feas for feature extraction. \ingroup FeatureExtractionFxp

/**
 * @brief Vector Multiplication and Accumulation operation using MAU .
 * @param[in] vector_1_data: pointer to the data of the M vector 1 (with M the number of vector pairs(vect1 and 2))
 * @param[in] vector_2_data: pointer to the data of the M vector 2
 * @param[out] result: pointer to the data of the M results
 * @param[in] vector_length: N : Numbers of points in vectors
 **/
void sif_feature_math_mac(int32_t *vector_1_data, int32_t *vector_2_data, int64_t *result,
                          uint16_t vector_length);

/** \brief  Resets time-domain feature extraction state.
	\param[in] statistic_state: pointer to statistics_state_t structure that contains intermediate data used for time feature extraction
	\param[in] pmean: pointer to the data mean
	\ingroup FeatureExtractionFxp
*/
int32_t SIF_TimeStatistics_ResetState(statistics_state_t *statistic_state, int32_t *pmean);

/** \brief  Initializes the feature extraction common settings.
    \param[in, out] config: pointer to config_common_t structure that holds common settings used for feature extraction
    \param[in] win_size: window size in number of samples
	\param[in] tconfigs_num: number of time configs
    \ingroup FeatureExtractionFxp
*/
void SIF_CommonConfig_Init(config_common_t *config, int32_t win_size, int32_t tconfigs_num);

/** \brief  Initializes the time-domain feature extraction settings.
	\param[in, out] config: pointer to config_stats_t structure that holds settings used for time-domain feature extraction
	\param[in] inv_win_size: inverse of window size in number of samples
	\param[in] hyst_thr_q16: hysteresis thresh
	\param[in] min_peak_dist: minimum peak distance in number of samples
	\param[in] min_peak_height: min peak height in q16
	\ingroup FeatureExtractionFxp
*/
void SIF_TemporalConfig_Init(config_time_t *config, int32_t inv_win_size, int32_t hyst_thr_q16,
                             int32_t min_peak_dist, int32_t min_peak_height);

/** \brief  initialize digital filter.
	\param[in, out] filter: pointer to filter_state_t structure that contains filter coefficients and data history buffer
	\param[in] num_coef: filter coefficients size
	\param[in] FiltBnA_Q28: filter coefficients arranged as [B_Q28, -A_Q28]. Fixed point format is Q28
	\ingroup FeatureExtractionFxp
*/
void SIF_Filter_Init(filter_state_t *filter, int32_t num_coef, const int32_t FiltBnA_Q28[]);

/** \brief  Resets filter's data buffer.
    \param[in, out] filter: pointer to filter_state_t structure that contains filter coefficients and data history buffer
    \ingroup FeatureExtractionFxp
*/
void SIF_Filter_ResetState(filter_state_t *filter);

/** \brief  Resets features state.
    \param[in, out] state: pointer to features_state_t structure that contains feature extraction data
    \return : 0 success 
    \ingroup FeatureExtractionFxp
*/
int32_t SIF_Features_ResetState(features_state_t *state);

#ifdef __cplusplus
}
#endif

#endif //FEATURE_EXTRACT_IR_