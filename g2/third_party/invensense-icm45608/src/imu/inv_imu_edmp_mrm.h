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

/** @defgroup MRM EDMP MRM
 *  @brief High-level functions to drive eDMP MRM
 *  @{
 */

/** @file inv_imu_edmp_mrm.h */

#ifndef _INV_IMU_EDMP_MRM_H_
#define _INV_IMU_EDMP_MRM_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "imu/inv_imu_driver.h"

/** @brief System usecase definition for IMU EDMP MRM initialization */
typedef enum { INV_IMU_EDMP_MRM_INIT_OVER_SIF } inv_imu_edmp_mrm_init_t;

/** @brief IMU MRM inputs parameters definition
 *  @note Refer to the AppNote for details on how to configure these parameters.
 */
typedef struct {
	uint32_t mrm_coarse_stab_cnt_thr;
	uint32_t mrm_fine_stab_cnt_thr;
	uint32_t mrm_large_instability_cnt;
	uint32_t mrm_small_instability_cnt;
	uint32_t mrm_stab_obs_window_cnt;
} inv_imu_edmp_mrm_parameters_t;

/** @brief Initialize automatic or on-demand MRM, this loads EDMP RAM image at RAM location depending on usecase.
 *  @param[in] s          Pointer to device.
 *  @param[in] usecase    System usecase for which MRM image is to be initialized.
 *  @return               0 on success, negative value on error.
 *  @warning              This must be called after inv_imu_edmp_gaf_init() and before enabling EDMP.
 */
int inv_imu_edmp_mrm_init(inv_imu_device_t *s, inv_imu_edmp_mrm_init_t usecase);

/** @brief Returns current EDMP parameters for RAM MRM algorithm.
 *  @param[in] s   Pointer to device.
 *  @param[out] p  The current parameters read from registers.
 *  @return        0 on success, negative value on error.
 */
int inv_imu_edmp_mrm_get_parameters(inv_imu_device_t *s, inv_imu_edmp_mrm_parameters_t *p);

/** @brief Configures EDMP parameters for RAM MRM algorithm.
 *  @warning This function should be called only when RAM MRM algorithm is disabled.
 *  @param[in] s  Pointer to device.
 *  @param[in] p  The requested input parameters.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_mrm_set_parameters(inv_imu_device_t *s, const inv_imu_edmp_mrm_parameters_t *p);

/** @brief Enable automatic MRM to be run by EDMP whenever specific conditions are met.
 *  @param[in] s          Pointer to device.
 *  @return               0 on success, negative value on error.
 *  @warning              This must be called after inv_imu_edmp_mrm_init() and before enabling EDMP.
 */
int inv_imu_edmp_mrm_enable_auto(inv_imu_device_t *s);

/** @brief Disable automatic MRM to be run by EDMP, only on-demand MRM will be run through inv_imu_edmp_mrm_request().
 *  @param[in] s          Pointer to device.
 *  @return               0 on success, negative value on error.
 *  @warning              This must be called after inv_imu_edmp_mrm_init() and before enabling EDMP.
 */
int inv_imu_edmp_mrm_disable_auto(inv_imu_device_t *s);

/** @brief Requests EDMP to trigger MRM operation at next EDMP ODR.
 *  @param[in] s Pointer to device.
 *  @return      0 on success, negative value on error.
 */
int inv_imu_edmp_mrm_request(inv_imu_device_t *s);

#ifdef __cplusplus
}
#endif

#endif /* _INV_IMU_EDMP_MRM_H_ */

/** @} */
