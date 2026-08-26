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

/** @defgroup EXT_FEATURES EDMP extended features
 *  @brief High-level functions to drive eDMP extended features
 *  @{
 */

/** @file inv_imu_edmp_extended_features.h */

#ifndef _INV_IMU_EXTENDED_FEATURES_H_
#define _INV_IMU_EXTENDED_FEATURES_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "imu/inv_imu_driver.h"

/** @brief IMU B2S parameters definition
 */
typedef struct {
	/* B2S */
	uint8_t b2s_mounting_matrix; /**< Specifies mounting matrix to be applied to B2S raw data
                                       Set bit 2 : swap X/Y ; flip Z
                                       Set bit 1 : flip X ; flip Z
                                       Set bit 0 : flip Y ; flip Z */
	int32_t
	         dev_norm_max; /**< Hysteresis added or removed to norm estimate and Y axis constrains value for RevB2S

                                         Unit in LSB, with 1 LBS = 1g / 2^12
                                         Default value 700 (corresponding to 0.1709g)
                                         Recommended range value [1 - 2048] */
	int32_t  sin_limit; /**< Maximum threshold on absolute value of X axis in b2s position
                                         link to the sinus value of inclination angle on X axis
                                         Unit in LSB, with 1 LBS = 1g / 2^12
                                         Default value 2048 (corresponding to 30deg)
                                         Recommended range value [300 - 3000] */
	int32_t  fast_limit; /**< Threshold of minimal motion to be detected as "Fast motion"
                                         Unit is no unit, filtered data
                                         Default value 200 */
	uint16_t fast_motion_age_limit; /**< Time limit between last "Fast motion" and b2s position
                                         Unit in sample number - ODR dependent
                                         Default value 20 (corresponding to 400ms at 50Hz) */
	uint16_t
	         fast_motion_time_limit; /**< Minimum time where the criterion is above the threshold  to be classified as "Fast motion"

                                         Unit in sample number - ODR dependent
                                         Default value 4 (corresponding to 80ms at 50Hz) */
	uint16_t age_limit; /**< Minimum time between 2 event b2s
                                         Unit in sample number - ODR dependent
                                         Default value 50 (corresponding to 1s at 50Hz) */
	uint16_t
	    rev_latency_th; /**< Condition of RevB2S should be maintained at least during RevB2sLatencyTh

                                         Unit in sample number - ODR dependent
                                         Default value 25 (corresponding to 0.5s at 50Hz) */
	int32_t
	    static_limit; /**< Threshold to determine static phase required after the gesture B2S to validate it

                                         Unit is no unit, filtered data
                                         Default value 1400 */
	int32_t
	    thr_cos_ang; /**< RevB2S threshold, condition satisfied when moving away from bring2see orientation position

                                         by more than threshold angle corresponding to the cosine angle
                                         Unit is cosine value of angle in q30
                                         Default value 1057429273 corresponding to 10deg */
	int32_t
	    rev_x_limit; /**< Condition of RevB2S on X axis value to ensure Rev-B2S when arm point down

                                         * Unit in LSB, with 1 LBS = 1g / 2^12
                                         * Default value 3680 (corresponding to 0.8984g)
                                         */
	uint32_t
	    sin_flat_angle; /**< Condition to detect the flat position and reject B2S interrupt at return to rest position

                                         Unit in LSB, with 1 LBS = 1g / 2^12
                                         Default value 2048 (corresponding to 30°) */
	uint32_t
	    timer_flat_reject; /**< A timer to disable flat rejection when age of the last no-flat B2S detection is over the timer

                                         Unit in sample number - ODR dependent
                                         Default value 350 (corresponding to 7s at 50Hz) */
} inv_imu_edmp_b2s_parameters_t;

/** @brief System usecase definition for IMU EDMP B2S initialization */
typedef enum {
	INV_IMU_EDMP_B2S_INIT_OVER_SIF,
	INV_IMU_EDMP_B2S_INIT_OVER_GAF
} inv_imu_edmp_b2s_init_t;

/** @brief  Initialize B2S algorithm for usecase where no SIF is needed. 
 *  @param[in]  s        Pointer to device.
 *  @param[out] usecase  System usecase for which B2S image was initialized.
 *  @return     0 on success, negative value on error.
 *  @warning inv_imu_edmp_init() must be called beforehand and can not be called anymore unless this API is called afterwards
 */
int inv_imu_edmp_b2s_init_over_sif(inv_imu_device_t *s, inv_imu_edmp_b2s_init_t *usecase);

/** @brief  Initialize B2S algorithm for usecase where no GAF is needed. 
 *  @param[in]  s        Pointer to device.
 *  @param[out] usecase  System usecase for which B2S image was initialized.
 *  @return     0 on success, negative value on error.
 *  @warning inv_imu_edmp_init() must be called beforehand and can not be called anymore unless this API is called afterwards
 */
int inv_imu_edmp_b2s_init_over_gaf(inv_imu_device_t *s, inv_imu_edmp_b2s_init_t *usecase);

/** @brief  Get current B2S configuration settings. 
 *  @param[in]  s           Pointer to device.
 *  @param[out] b2s_params  Pointer to B2S configuration structure, which will hold current B2S configuration.
 *  @param[in]  usecase     System usecase for which B2S image was initialized.
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_b2s_get_parameters(inv_imu_device_t *s, inv_imu_edmp_b2s_parameters_t *b2s_params,
                                    inv_imu_edmp_b2s_init_t usecase);

/** @brief  Set new B2S configuration settings. 
 *  @param[in]  s           Pointer to device.
 *  @param[in]  b2s_params  Pointer to B2S configuration structure, which contains new B2S configuration.
 *  @param[in]  usecase     System usecase for which B2S image was initialized.
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_b2s_set_parameters(inv_imu_device_t *                   s,
                                    const inv_imu_edmp_b2s_parameters_t *b2s_params,
                                    inv_imu_edmp_b2s_init_t              usecase);

/** @brief  Enable APEX algorithm B2S. 
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_b2s_enable(inv_imu_device_t *s);

/** @brief  Disable APEX algorithm B2S.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_b2s_disable(inv_imu_device_t *s);

/** @brief IMU AID inputs parameters definition for one AID instance
 */
struct aid_parameters_s {
	uint32_t aid_update_win; /**< Window time use to take a decision
							  Activity or inactivity will trigger after this updateWin window
							  Unit is sample number
							  Default value 150, corresponding 3s at 50Hz */
	uint32_t aid_alert_timer; /**< Timer since the last Activity event used to trig sedendaty alert 
							    Unit is sample number
							    Default value 90000, corresponding 30min at 50Hz */
	uint8_t  aid_output_enable; /**< Bitwise enable output 
									Unit is no unit, Bit 1 for enable activity detection, bit 2 for inactivity, bit 3 for alert
									Default value 7, corresponding all output enable */
	uint8_t  aid_disable_multiple_interrupt; /**< Option to disable output after each internal decision of algorithm
												means that output will trigger after each window time corresponding to updateWin
												Unit is no unit, acceptable value is 0 or 1
												Default value 0, corresponding to all decision are triggered */
};

/** @brief IMU AID inputs parameters definition
 */
typedef struct {
	struct aid_parameters_s aid_human; /**< AID human instance */
	struct aid_parameters_s aid_device; /**< AID device instance */
} inv_imu_edmp_aid_parameters_t;

/** @brief System usecase definition for IMU EDMP AID initialization */
typedef enum {
	INV_IMU_EDMP_AID_INIT_OVER_SIF,
	INV_IMU_EDMP_AID_INIT_OVER_GAF
} inv_imu_edmp_aid_init_t;

/** @brief  Initialize AID algorithm for usecase where no SIF is needed. 
 *  @param[in]  s        Pointer to device.
 *  @param[out] usecase  System usecase for which AID image was initialized.
 *  @return     0 on success, negative value on error.
 *  @warning inv_imu_edmp_init() must be called beforehand and can not be called anymore unless this API is called afterwards
 */
int inv_imu_edmp_aid_init_over_sif(inv_imu_device_t *s, inv_imu_edmp_aid_init_t *usecase);

/** @brief  Initialize AID algorithm for usecase where no GAF is needed. 
 *  @param[in]  s        Pointer to device.
 *  @param[out] usecase  System usecase for which AID image was initialized.
 *  @return     0 on success, negative value on error.
 *  @warning inv_imu_edmp_init() must be called beforehand and can not be called anymore unless this API is called afterwards
 */
int inv_imu_edmp_aid_init_over_gaf(inv_imu_device_t *s, inv_imu_edmp_aid_init_t *usecase);

/** @brief  Get current AID configuration settings. 
 *  @param[in]  s           Pointer to device.
 *  @param[out] aid_params  Pointer to AID configuration structure, which will hold current AID configuration.
 *  @param[in]  usecase     System usecase for which AID image was initialized.
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_aid_get_parameters(inv_imu_device_t *s, inv_imu_edmp_aid_parameters_t *aid_params,
                                    inv_imu_edmp_aid_init_t usecase);

/** @brief  Set new AID configuration settings. 
 *  @param[in]  s           Pointer to device.
 *  @param[in]  aid_params  Pointer to AID configuration structure, which contains new AID configuration.
 *  @param[in]  usecase     System usecase for which AID image was initialized.
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_aid_set_parameters(inv_imu_device_t *                   s,
                                    const inv_imu_edmp_aid_parameters_t *aid_params,
                                    inv_imu_edmp_aid_init_t              usecase);

/** @brief  Enable AID algorithm. 
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_aid_enable(inv_imu_device_t *s);

/** @brief  Disable AID algorithm.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_aid_disable(inv_imu_device_t *s);

/** @brief  Retrieve the current output state of the AID human instance
 *  @param[in] s              Pointer to device.
 *  @param[in] usecase        System usecase for which AID image was initialized.
 *  @param[out] output_state  AID human instance current output state
 *  @return                   0 on success, negative value on error.
 */
int inv_imu_edmp_aid_get_data_human(inv_imu_device_t *s, inv_imu_edmp_aid_init_t usecase,
                                    uint8_t *output_state);

/** @brief  Retrieve the current output state of the AID device instance
 *  @param[in] s              Pointer to device.
 *  @param[in] usecase        System usecase for which AID image was initialized.
 *  @param[out] output_state  AID device instance current output state
 *  @return                   0 on success, negative value on error.
 */
int inv_imu_edmp_aid_get_data_device(inv_imu_device_t *s, inv_imu_edmp_aid_init_t usecase,
                                     uint8_t *output_state);

#ifdef __cplusplus
}
#endif

#endif /* _INV_IMU_EXTENDED_FEATURES_H_ */

/** @} */
