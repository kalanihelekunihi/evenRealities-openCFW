/*
 * ________________________________________________________________________________________________________
 * Copyright (c) 2021 InvenSense Inc. All rights reserved.
 *
 * This software, related documentation and any modifications thereto (collectively "Software") is subject
 * to InvenSense and its licensors' intellectual property rights under U.S. and international copyright
 * and other intellectual property rights laws.
 *
 * InvenSense and its licensors retain all intellectual property and proprietary rights in and to the Software
 * and any use, reproduction, disclosure or distribution of the Software without an express license agreement
 * from InvenSense is strictly prohibited.
 *
 * EXCEPT AS OTHERWISE PROVIDED IN A LICENSE AGREEMENT BETWEEN THE PARTIES, THE SOFTWARE IS
 * PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
 * TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.
 * EXCEPT AS OTHERWISE PROVIDED IN A LICENSE AGREEMENT BETWEEN THE PARTIES, IN NO EVENT SHALL
 * INVENSENSE BE LIABLE FOR ANY DIRECT, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
 * NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
 * OF THE SOFTWARE.
 *
 * ________________________________________________________________________________________________________
 */

#ifndef __INV_IMU_EDMP_DEFS_H__
#define __INV_IMU_EDMP_DEFS_H__

#ifdef __cplusplus
extern "C" {
#endif

#define EDMP_RAM_BASE	0x0
#define EDMP_ROM_BASE	0x4000
#define EDMP_ROM_DATA_SIZE	0x1800
#define EDMP_APEX_FEATURE_STACK_END	0x200
#define EDMP_PATCH_TABLE_START	0x48
#define EDMP_PATCH_TABLE_END	0xDC
#define RAM_MRM_IMG_DATA_BASE	0x9DC
#define RAM_MRM_IMG_PRGM_BASE	0xA24
#define RAM_AUTHEN_IMG_PRGM_BASE	0x54
#define RAM_AUTHEN_IMG_STACK_END	0x300
#define RAM_SELFTEST_IMG_PRGM_BASE	0x100
#define RAM_SELFTEST_IMG_STACK_END	0xB00
#define RAM_B2S_IMG_DATA_BASE	0x1000
#define RAM_B2S_OVER_GAF_IMG_DATA_BASE	0x264
#define RAM_DISPATCH_PRGM_BASE	0x1580
#define RAM_DISPATCH_OVER_GAF_PRGM_BASE	0x7E4
#define RAM_AID_IMG_DATA_BASE	0x1600
#define RAM_AID_OVER_GAF_IMG_DATA_BASE	0x800
#define RAM_ALL_QUAT_IMG_DATA_BASE	0xD00
#define RAM_CALMAG_IMG_PRGM_BASE	0xC80
#define EDMP_HOST_INT_TAP_DET_POS	0x0
#define EDMP_HOST_INT_HIGHG_DET_POS	0x1
#define EDMP_HOST_INT_LOWG_DET_POS	0x2
#define EDMP_HOST_INT_ML_POS	0x3
#define EDMP_HOST_INT_MRM_CHG_POS	0x4
#define EDMP_HOST_INT_MRM_RUN_POS	0x5
#define EDMP_HOST_INT_FF_DET_POS	0x6
#define EDMP_HOST_INT_B2S_DET_POS	0x7
#define EDMP_HOST_INT_REVB2S_DET_POS	0x0
#define EDMP_HOST_INT_MRM_THR_POS	0x1
#define EDMP_HOST_INT_AID_HUMAN_POS	0x5
#define EDMP_HOST_INT_AID_DEVICE_POS	0x6
#define EDMP_HOST_INT_SELF_TEST_DONE_POS	0x2
#define EDMP_HOST_INT_SA_DONE_POS	0x4
#define EDMP_HOST_DISABLE_GAF	0x2
#define EDMP_HOST_DISABLE_FF	0x8
#define EDMP_HOST_DISABLE_TAP	0x10
#define EDMP_ONDEMAND_ENABLE_MEMSET	0x1
#define EDMP_ONDEMAND_ENABLE_GAF_PARAM	0x2
#define EDMP_ONDEMAND_ENABLE_GAF_BIAS	0x4


#ifdef __cplusplus
}
#endif

#endif // __INV_IMU_EDMP_DEFS_H__
