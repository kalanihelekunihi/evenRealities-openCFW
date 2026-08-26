/*
 *
 * Copyright (c) [2024] by InvenSense, Inc.
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

#ifndef __INV_IMU_EDMPRAM_MRM_MEMMAP_MEMMAP_H__
#define __INV_IMU_EDMPRAM_MRM_MEMMAP_MEMMAP_H__

#ifdef __cplusplus
extern "C" {
#endif

/* mrm_coarse_stab_cnt_thr
 *
 * Number of samples used to identify "coarse" stability condition.
 * Default value 100 (corresponding to 1s at 100Hz)
 */
#define EDMP_MRM_COARSE_STAB_CNT_THR                            0xa00
#define EDMP_MRM_COARSE_STAB_CNT_THR_SIZE                       4

/* mrm_fine_stab_cnt_thr
 *
 * Number of samples used to identify "fine" stability condition.
 * Default value 1 (corresponding to 10ms at 100Hz)
 */
#define EDMP_MRM_FINE_STAB_CNT_THR                              0xa0c
#define EDMP_MRM_FINE_STAB_CNT_THR_SIZE                         4

/* mrm_large_instability_cnt
 *
 * Number of samples during which large instabilities are tolerated (MRM side-effects).
 * Default value 100 (corresponding to 1s at 100Hz)
 */
#define EDMP_MRM_LARGE_INSTABILITY_CNT                          0xa10
#define EDMP_MRM_LARGE_INSTABILITY_CNT_SIZE                     4

/* mrm_small_instability_cnt
 *
 * Number of samples during which small instabilities are tolerated (MRM side-effects).
 * Default value 1500 (corresponding to 15s at 100Hz)
 */
#define EDMP_MRM_SMALL_INSTABILITY_CNT                          0xa14
#define EDMP_MRM_SMALL_INSTABILITY_CNT_SIZE                     4

/* mrm_stab_obs_window_cnt
 *
 * Number of samples defining the window before updating the "golden" reference.
 * Default value 100 (corresponding to 1s at 100Hz)
 */
#define EDMP_MRM_STAB_OBS_WINDOW_CNT                            0xa18
#define EDMP_MRM_STAB_OBS_WINDOW_CNT_SIZE                       4

#ifdef __cplusplus
}
#endif

#endif // __INV_IMU_EDMPRAM_MRM_MEMMAP_MEMMAP_H__
